"""
block_data_preview.py
─────────────────────
Interactive import-prep tool.

For every unique unresolved value (block, variety, rootstock) it pops up a
window asking the user to pick the correct DB record from a dropdown.
For any row whose structure is ambiguous (side vs portion) it asks the user.

Mappings are remembered — each unique raw value is only asked once.
Results are written to:
  block_rows_preview.csv
  row_portions_preview.csv
"""

import csv
import re
import statistics
import tkinter as tk
from collections import defaultdict
from tkinter import ttk, messagebox

import openpyxl
import requests

BASE_URL = "http://192.168.1.7:8000"

# ─────────────────────────────────────────────
# API
# ─────────────────────────────────────────────

def api_get(path):
    resp = requests.get(f"{BASE_URL}{path}")
    resp.raise_for_status()
    return resp.json()

def load_api_lookups():
    blocks     = [(r["name"], r["id"]) for r in api_get("/blocks/")]
    varieties  = [(r["name"], r["id"]) for r in api_get("/varieties/")]
    rootstocks = [(r["name"], r["id"]) for r in api_get("/rootstocks/")]
    return blocks, varieties, rootstocks

# ─────────────────────────────────────────────
# Year cleaning
# ─────────────────────────────────────────────

def clean_year(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s == " ":
        return None
    try:
        val = int(float(s))
    except ValueError:
        return None
    if val >= 1900:
        return val
    return 2000 + val if val <= 30 else 1900 + val

# ─────────────────────────────────────────────
# Side vs Portion detection
# ─────────────────────────────────────────────

def detect_structure(group_lengths, block_row_lengths):
    if len(group_lengths) < 2:
        return "PORTION"
    if not block_row_lengths:
        return "AMBIGUOUS"
    med        = statistics.median(block_row_lengths)
    total      = sum(l for l in group_lengths if l)
    avg_indiv  = statistics.mean(abs((l or 0) - med) for l in group_lengths)
    total_diff = abs(total - med)
    if total_diff < avg_indiv:
        return "PORTION"
    elif avg_indiv < total_diff:
        return "SIDE"
    return "AMBIGUOUS"

# ─────────────────────────────────────────────
# Interactive mapping popup
# ─────────────────────────────────────────────

SKIP   = "__SKIP__"
CANCEL = "__CANCEL__"

def ask_mapping(root, field_label, raw_value, options, context_info=""):
    """
    Returns (name, id), (SKIP, SKIP), or (CANCEL, CANCEL).
    """
    result = {"name": CANCEL, "id": CANCEL}

    win = tk.Toplevel(root)
    win.title(f"Map {field_label}")
    win.resizable(False, False)
    win.grab_set()

    pad = {"padx": 12, "pady": 6}

    tk.Label(win, text=f"Spreadsheet {field_label}:", font=("Helvetica", 10, "bold")).grid(
        row=0, column=0, sticky="w", **pad)
    tk.Label(win, text=raw_value, font=("Helvetica", 11), fg="#b03020").grid(
        row=0, column=1, sticky="w", **pad)

    if context_info:
        tk.Label(win, text=context_info, font=("Helvetica", 9), fg="#555555").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 4))

    tk.Label(win, text=f"Matches to DB {field_label}:").grid(
        row=2, column=0, sticky="w", **pad)

    display_names = ["— Skip / None —"] + [name for name, _ in options]
    id_map        = {name: id_ for name, id_ in options}

    var = tk.StringVar(value=display_names[0])
    cb  = ttk.Combobox(win, textvariable=var, values=display_names,
                       state="readonly", width=40)
    cb.grid(row=2, column=1, sticky="w", **pad)

    def confirm():
        chosen = var.get()
        if chosen == "— Skip / None —":
            result["name"] = SKIP
            result["id"]   = SKIP
        else:
            result["name"] = chosen
            result["id"]   = id_map[chosen]
        win.destroy()

    def skip():
        result["name"] = SKIP
        result["id"]   = SKIP
        win.destroy()

    def cancel():
        result["name"] = CANCEL
        result["id"]   = CANCEL
        win.destroy()

    # Closing the window via the X button = cancel
    win.protocol("WM_DELETE_WINDOW", cancel)

    btn_frame = tk.Frame(win)
    btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(btn_frame, text="Confirm",     width=12, command=confirm,
              bg="#3a7ebf", fg="white").pack(side="left", padx=6)
    tk.Button(btn_frame, text="Skip / None", width=12, command=skip).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Cancel All",  width=12, command=cancel,
              bg="#b03020", fg="white").pack(side="left", padx=6)

    win.wait_window()
    return result["name"], result["id"]


def ask_structure(root, block_raw, row_number, lengths, median_len):
    """Returns 'SIDE', 'PORTION', or CANCEL."""
    result = {"answer": CANCEL}

    win = tk.Toplevel(root)
    win.title("Side or Portion?")
    win.resizable(False, False)
    win.grab_set()

    pad = {"padx": 12, "pady": 6}

    tk.Label(win, text="Ambiguous row structure", font=("Helvetica", 11, "bold")).pack(**pad)
    tk.Label(win, text=f"Block: {block_raw}   Row: {row_number}", font=("Helvetica", 10)).pack(padx=12)
    tk.Label(win, text=f"Lengths in this group: {[round(l,1) if l else None for l in lengths]}",
             font=("Helvetica", 9), fg="#555").pack(padx=12)
    tk.Label(win, text=f"Median row length for this block: {round(median_len,1) if median_len else '?'}",
             font=("Helvetica", 9), fg="#555").pack(padx=12, pady=(0, 8))
    tk.Label(win, text=(
        "SIDE  → each entry is a separate side of the same physical row\n"
        "PORTION → entries are portions along one row (different varieties/years)"
    ), font=("Helvetica", 9), justify="left").pack(padx=12, pady=(0, 10))

    def pick(val):
        result["answer"] = val
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", lambda: pick(CANCEL))

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="SIDE",       width=14, command=lambda: pick("SIDE"),
              bg="#3a7ebf", fg="white").pack(side="left", padx=6)
    tk.Button(btn_frame, text="PORTION",    width=14, command=lambda: pick("PORTION"),
              bg="#5a9e5a", fg="white").pack(side="left", padx=6)
    tk.Button(btn_frame, text="Cancel All", width=14, command=lambda: pick(CANCEL),
              bg="#b03020", fg="white").pack(side="left", padx=6)

    win.wait_window()
    return result["answer"]

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.withdraw()

    print("Loading lookups from API…")
    try:
        db_blocks, db_varieties, db_rootstocks = load_api_lookups()
    except Exception as e:
        messagebox.showerror("API Error", f"Could not reach API:\n{e}", parent=root)
        return
    print(f"  {len(db_blocks)} blocks, {len(db_varieties)} varieties, {len(db_rootstocks)} rootstocks")

    wb = openpyxl.load_workbook("BLOCK DATA.xlsx", data_only=True)
    ws = wb["Sheet1"]

    raw_rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        block, row_no, variety, rs, year, row_width, _, tree_no, row_len, _, area, _ = row
        if not block or str(block).strip() == "" or row_no is None:
            continue
        raw_rows.append({
            "block_raw":   str(block).strip(),
            "row_number":  int(row_no),
            "variety_raw": str(variety).strip() if variety else None,
            "rs_raw":      str(rs).strip() if rs is not None else None,
            "year_raw":    year,
            "row_width":   row_width,
            "tree_count":  int(tree_no) if tree_no else None,
            "row_length":  float(row_len) if row_len else None,
            "area_m2":     float(area) if area else None,
        })

    # Collect unique values
    # Block mapping is keyed on (block_raw, variety_raw) so that the same
    # block name with different varieties can map to different DB blocks
    # (e.g. "Cherries" + "Chelan" vs "Cherries" + "Van")
    unique_block_variety = sorted({
        (r["block_raw"], r["variety_raw"] or "") for r in raw_rows
    })
    unique_varieties = sorted({r["variety_raw"] for r in raw_rows if r["variety_raw"]})
    unique_rs        = sorted({r["rs_raw"] for r in raw_rows if r["rs_raw"]})

    total_steps = len(unique_block_variety) + len(unique_varieties) + len(unique_rs)
    step = [0]

    def progress(label):
        step[0] += 1
        print(f"  [{step[0]}/{total_steps}] {label}")

    # ── Ask user to map each unique (block, variety) combination ──
    block_map = {}   # (block_raw, variety_raw) → (matched_name, matched_id)
    print(f"\nAsking about {len(unique_block_variety)} block+variety combinations…")
    for block_raw, variety_raw in unique_block_variety:
        context = f"Variety in this row: {variety_raw}" if variety_raw else ""
        label   = f"{block_raw}  +  {variety_raw}" if variety_raw else block_raw
        progress(f"Block combo: {label}")
        name, id_ = ask_mapping(root, "Block", label, db_blocks, context_info=context)
        if name == CANCEL:
            print("Cancelled by user.")
            root.destroy()
            return
        block_map[(block_raw, variety_raw)] = (name, id_)

    # ── Ask user to map each unique variety ───────────────────────
    variety_map = {}
    print(f"\nAsking about {len(unique_varieties)} unique variety names…")
    for raw in unique_varieties:
        progress(f"Variety: {raw}")
        name, id_ = ask_mapping(root, "Variety", raw, db_varieties)
        if name == CANCEL:
            print("Cancelled by user.")
            root.destroy()
            return
        variety_map[raw] = (name, id_)

    # ── Ask user to map each unique rootstock ─────────────────────
    rs_map = {}
    print(f"\nAsking about {len(unique_rs)} unique rootstock codes…")
    for raw in unique_rs:
        progress(f"Rootstock: {raw}")
        name, id_ = ask_mapping(root, "Rootstock", raw, db_rootstocks)
        if name == CANCEL:
            print("Cancelled by user.")
            root.destroy()
            return
        rs_map[raw] = (name, id_)

    # ── Group rows by (block, row_number) ─────────────────────────
    groups = defaultdict(list)
    for r in raw_rows:
        groups[(r["block_raw"], r["row_number"])].append(r)

    # Per-block median row length
    block_lengths = defaultdict(list)
    for (block, _), entries in groups.items():
        if len(entries) == 1 and entries[0]["row_length"]:
            block_lengths[block].append(entries[0]["row_length"])

    # ── Ask about ambiguous structures ────────────────────────────
    structure_map = {}
    ambiguous_keys = [
        (block_raw, row_number, [e["row_length"] for e in entries])
        for (block_raw, row_number), entries in sorted(groups.items())
        if detect_structure([e["row_length"] for e in entries], block_lengths[block_raw]) == "AMBIGUOUS"
    ]

    if ambiguous_keys:
        print(f"\nAsking about {len(ambiguous_keys)} ambiguous row structures…")
    for block_raw, row_number, lengths in ambiguous_keys:
        ref = block_lengths[block_raw]
        med = statistics.median(ref) if ref else None
        answer = ask_structure(root, block_raw, row_number, lengths, med)
        if answer == CANCEL:
            print("Cancelled by user.")
            root.destroy()
            return
        structure_map[(block_raw, row_number)] = answer

    # ── Build output records ───────────────────────────────────────
    block_rows_out   = []
    row_portions_out = []
    seen_block_rows  = set()

    for (block_raw, row_number), entries in sorted(groups.items()):
        lengths   = [e["row_length"] for e in entries]
        structure = detect_structure(lengths, block_lengths[block_raw])
        if structure == "AMBIGUOUS":
            structure = structure_map.get((block_raw, row_number), "PORTION")
        row_width = entries[0]["row_width"]

        if structure == "SIDE":
            for entry in entries:
                variety_key = entry["variety_raw"] or ""
                b_name, b_id = block_map.get((block_raw, variety_key), (SKIP, SKIP))
                side    = "N"
                row_key = (b_id, row_number, side)

                if row_key not in seen_block_rows:
                    seen_block_rows.add(row_key)
                    block_rows_out.append({
                        "block_raw":     block_raw,
                        "block_matched": b_name if b_name != SKIP else "",
                        "block_id":      b_id   if b_id   != SKIP else "",
                        "row_number":    row_number,
                        "side":          side,
                        "row_length_m":  entry["row_length"] or "",
                        "row_width_m":   row_width or "",
                        "structure":     "SIDE",
                    })

                v_name, v_id = variety_map.get(variety_key, (SKIP, SKIP))
                r_name, r_id = rs_map.get(entry["rs_raw"] or "", (SKIP, SKIP))

                row_portions_out.append({
                    "block_raw":         block_raw,
                    "block_matched":     b_name if b_name != SKIP else "",
                    "row_number":        row_number,
                    "side":              side,
                    "structure":         "SIDE",
                    "variety_raw":       variety_key,
                    "variety_matched":   v_name if v_name != SKIP else "",
                    "variety_id":        v_id   if v_id   != SKIP else "",
                    "rootstock_raw":     entry["rs_raw"] or "",
                    "rootstock_matched": r_name if r_name != SKIP else "",
                    "rootstock_id":      r_id   if r_id   != SKIP else "",
                    "planting_year":     clean_year(entry["year_raw"]) or "",
                    "tree_count":        entry["tree_count"] or "",
                    "length_m":          entry["row_length"] or "",
                    "area_m2":           entry["area_m2"] or "",
                })

        else:  # PORTION
            total_len = sum(l for l in lengths if l) or None
            # Use the first entry's variety to look up the block
            first_variety = entries[0]["variety_raw"] or ""
            b_name, b_id = block_map.get((block_raw, first_variety), (SKIP, SKIP))
            row_key = (b_id, row_number, None)

            if row_key not in seen_block_rows:
                seen_block_rows.add(row_key)
                block_rows_out.append({
                    "block_raw":     block_raw,
                    "block_matched": b_name if b_name != SKIP else "",
                    "block_id":      b_id   if b_id   != SKIP else "",
                    "row_number":    row_number,
                    "side":          "",
                    "row_length_m":  total_len or "",
                    "row_width_m":   row_width or "",
                    "structure":     "PORTION",
                })

            for entry in entries:
                variety_key = entry["variety_raw"] or ""
                v_name, v_id = variety_map.get(variety_key, (SKIP, SKIP))
                r_name, r_id = rs_map.get(entry["rs_raw"] or "", (SKIP, SKIP))

                row_portions_out.append({
                    "block_raw":         block_raw,
                    "block_matched":     b_name if b_name != SKIP else "",
                    "row_number":        row_number,
                    "side":              "",
                    "structure":         "PORTION",
                    "variety_raw":       variety_key,
                    "variety_matched":   v_name if v_name != SKIP else "",
                    "variety_id":        v_id   if v_id   != SKIP else "",
                    "rootstock_raw":     entry["rs_raw"] or "",
                    "rootstock_matched": r_name if r_name != SKIP else "",
                    "rootstock_id":      r_id   if r_id   != SKIP else "",
                    "planting_year":     clean_year(entry["year_raw"]) or "",
                    "tree_count":        entry["tree_count"] or "",
                    "length_m":          entry["row_length"] or "",
                    "area_m2":           entry["area_m2"] or "",
                })

    # ── Write CSVs ────────────────────────────────────────────────
    br_fields = ["block_raw", "block_matched", "block_id",
                 "row_number", "side", "row_length_m", "row_width_m", "structure"]
    with open("block_rows_preview.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=br_fields)
        w.writeheader()
        w.writerows(block_rows_out)

    rp_fields = ["block_raw", "block_matched", "row_number", "side", "structure",
                 "variety_raw", "variety_matched", "variety_id",
                 "rootstock_raw", "rootstock_matched", "rootstock_id",
                 "planting_year", "tree_count", "length_m", "area_m2"]
    with open("row_portions_preview.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rp_fields)
        w.writeheader()
        w.writerows(row_portions_out)

    print(f"\nDone.")
    print(f"  block_rows_preview.csv   → {len(block_rows_out)} rows")
    print(f"  row_portions_preview.csv → {len(row_portions_out)} rows")
    messagebox.showinfo("Done",
        f"Preview files written.\n\n"
        f"  block_rows_preview.csv   → {len(block_rows_out)} rows\n"
        f"  row_portions_preview.csv → {len(row_portions_out)} rows\n\n"
        "Review and correct any mappings, then run the bulk-import script.",
        parent=root)
    root.destroy()


if __name__ == "__main__":
    main()

