"""
block_data_import.py
────────────────────
Reads block_rows_preview.csv and row_portions_preview.csv and bulk-imports
them into the database via the Farm Master API.

Run AFTER reviewing and correcting the preview CSVs.

Usage:
    python block_data_import.py

Rows with empty block_id or variety_id are skipped and reported at the end.
Duplicate rows (409 Conflict) are also skipped gracefully.
"""

import csv
import sys
import requests

BASE_URL = "http://192.168.1.7:8000"

def api_post(path, payload):
    resp = requests.post(f"{BASE_URL}{path}", json=payload)
    if resp.status_code == 409:
        return None, "DUPLICATE"
    resp.raise_for_status()
    return resp.json(), None

def api_get(path, params=None):
    resp = requests.get(f"{BASE_URL}{path}", params=params or {})
    resp.raise_for_status()
    return resp.json()

def opt_str(v):
    return v.strip() if v and v.strip() else None

def opt_int(v):
    v = v.strip() if v else ""
    return int(v) if v else None

def opt_dec(v):
    v = v.strip() if v else ""
    return v if v else None

def main():
    # ── Load existing block_rows so we can look up IDs for portions ─
    print("Fetching existing block rows from API…")
    existing_rows = api_get("/block-rows/")
    # Key: (block_id, row_number, side_or_none) → row_id
    existing_map = {}
    for r in existing_rows:
        side = r["side"] or ""
        existing_map[(r["block_id"], r["row_number"], side)] = r["id"]

    # ── Import block_rows ──────────────────────────────────────────
    print("\nImporting block rows…")
    created_rows   = 0
    skipped_rows   = 0
    duplicate_rows = 0
    error_rows     = []

    # Track newly created rows: (block_id, row_number, side) → row_id
    new_row_map = {}

    with open("block_rows_preview.csv", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # start=2 for line numbers
            block_id   = opt_str(row["block_id"])
            row_number = opt_int(row["row_number"])
            side       = opt_str(row["side"]) or ""

            if not block_id:
                skipped_rows += 1
                print(f"  SKIP  line {i}: no block_id  ({row['block_raw']} row {row_number})")
                continue

            # Check if already exists
            lookup_key = (block_id, row_number, side)
            if lookup_key in existing_map:
                duplicate_rows += 1
                new_row_map[lookup_key] = existing_map[lookup_key]
                continue

            payload = {
                "block_id":     block_id,
                "row_number":   row_number,
                "side":         side or None,
                "row_length_m": opt_dec(row["row_length_m"]),
                "row_width_m":  opt_dec(row["row_width_m"]),
                "notes":        None,
            }

            try:
                result, err = api_post("/block-rows/", payload)
                if err == "DUPLICATE":
                    # Fetch the real ID
                    matches = api_get("/block-rows/", params={"block_id": block_id})
                    match = next((r for r in matches
                                  if r["row_number"] == row_number
                                  and (r["side"] or "") == side), None)
                    if match:
                        new_row_map[lookup_key] = match["id"]
                    duplicate_rows += 1
                else:
                    new_row_map[lookup_key] = result["id"]
                    existing_map[lookup_key] = result["id"]
                    created_rows += 1
                    print(f"  CREATED block row: {row['block_matched']} row {row_number} side={side or 'NULL'}")
            except Exception as e:
                error_rows.append((i, row["block_raw"], row_number, str(e)))
                print(f"  ERROR  line {i}: {e}")

    print(f"\nBlock rows — created: {created_rows}, duplicates skipped: {duplicate_rows}, "
          f"missing block skipped: {skipped_rows}, errors: {len(error_rows)}")

    # Merge maps so portions can find all row IDs
    full_row_map = {**existing_map, **new_row_map}

    # ── Import row_portions ────────────────────────────────────────
    print("\nImporting row portions…")
    created_portions   = 0
    skipped_portions   = 0
    duplicate_portions = 0
    error_portions     = []

    # Build block_matched_name → block_id from the block_rows CSV
    block_name_to_id = {}
    with open("block_rows_preview.csv", newline="") as bf:
        for br in csv.DictReader(bf):
            if br["block_id"]:
                block_name_to_id[br["block_matched"]] = br["block_id"]

    # Pre-pass: assign sequence numbers per (block_name, row_number, side)
    # by counting occurrences in CSV order
    sequence_counters = {}
    portions_with_seq = []
    with open("row_portions_preview.csv", newline="") as f:
        for row in csv.DictReader(f):
            side       = opt_str(row["side"]) or ""
            row_number = opt_int(row["row_number"])
            block_name = opt_str(row["block_matched"])
            key = (block_name, row_number, side)
            sequence_counters[key] = sequence_counters.get(key, 0) + 1
            portions_with_seq.append((row, sequence_counters[key]))

    with open("row_portions_preview.csv", newline="") as f:
        for i, (row, seq) in enumerate(zip(csv.DictReader(f), [s for _, s in portions_with_seq]), start=2):
            variety_id = opt_str(row["variety_id"])
            clone_id   = opt_str(row.get("clone_id", ""))
            side       = opt_str(row["side"]) or ""
            row_number = opt_int(row["row_number"])
            block_name = opt_str(row["block_matched"])
            block_id   = block_name_to_id.get(block_name, "")

            if not variety_id:
                skipped_portions += 1
                print(f"  SKIP  line {i}: no variety_id  ({row['variety_raw']} in {block_name} row {row_number})")
                continue

            # Look up the row_id
            row_id = full_row_map.get((block_id, row_number, side))
            if not row_id:
                skipped_portions += 1
                print(f"  SKIP  line {i}: could not find row_id for "
                      f"{block_name} row {row_number} side='{side or 'NULL'}'")
                continue

            payload = {
                "row_id":        row_id,
                "variety_id":    variety_id,
                "clone_id":      clone_id or None,
                "rootstock_id":  opt_str(row["rootstock_id"]) or None,
                "planting_year": opt_int(row["planting_year"]),
                "tree_count":    opt_int(row["tree_count"]),
                "length_m":      opt_dec(row["length_m"]),
                "area_m2":       opt_dec(row["area_m2"]),
                "sequence_no":   seq,
            }
            payload = {k: v for k, v in payload.items() if v is not None}

            try:
                result, err = api_post("/row-portions/", payload)
                if err == "DUPLICATE":
                    duplicate_portions += 1
                else:
                    created_portions += 1
                    print(f"  CREATED portion: {block_name} row {row_number} "
                          f"— {row['variety_matched']} / {row['rootstock_matched']} {row['planting_year']}")
            except Exception as e:
                error_portions.append((i, block_name, row_number, str(e)))
                print(f"  ERROR  line {i}: {e}")

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("IMPORT COMPLETE")
    print(f"  Block rows   — created: {created_rows:>4}, "
          f"duplicates: {duplicate_rows:>4}, skipped: {skipped_rows:>4}, errors: {len(error_rows):>4}")
    print(f"  Row portions — created: {created_portions:>4}, "
          f"duplicates: {duplicate_portions:>4}, skipped: {skipped_portions:>4}, errors: {len(error_portions):>4}")

    if error_rows or error_portions:
        print("\nErrors:")
        for line, block, rn, msg in error_rows + error_portions:
            print(f"  line {line}: {block} row {rn} — {msg}")

    if error_rows or error_portions:
        sys.exit(1)

if __name__ == "__main__":
    main()


