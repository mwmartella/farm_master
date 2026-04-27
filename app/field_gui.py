"""
Field Management GUI
Manages the Fields database table.
Launched from the Santa Rita Control Panel.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import app.api_client as api
from app.org_gui import (
    FieldsTab,
    _apply_style,
    _maximize,
    _build_header,
    build_tree,
    EditDialog,
    _top,
)
from app.planting_gui import BlocksTab

SIDES = ["N", "S", "E", "W"]


class BlockRowsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._block_map     = {}
        self._variety_map   = {}
        self._clone_map     = {}
        self._rootstock_map = {}
        self._build_form()
        self._build_filter()
        self._build_controls()
        self._build_tree()
        self._load_lookups()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Block Row")
        form.pack(fill="x", padx=10, pady=(12, 0))

        r0 = ttk.Frame(form)
        r0.pack(fill="x", padx=10, pady=(8, 2))

        ttk.Label(r0, text="Block:").grid(row=0, column=0, sticky="e", padx=6, pady=3)
        self.block_var = tk.StringVar()
        self.block_cb = ttk.Combobox(r0, textvariable=self.block_var, state="readonly", width=20)
        self.block_cb.grid(row=0, column=1, sticky="w", padx=6, pady=3)

        ttk.Label(r0, text="Row #:").grid(row=0, column=2, sticky="e", padx=6, pady=3)
        self.row_num_entry = ttk.Entry(r0, width=6)
        self.row_num_entry.grid(row=0, column=3, sticky="w", padx=6, pady=3)

        ttk.Label(r0, text="Side:").grid(row=0, column=4, sticky="e", padx=6, pady=3)
        self.side_var = tk.StringVar(value="")
        self.side_cb = ttk.Combobox(r0, textvariable=self.side_var,
                                    values=[""] + SIDES, state="readonly", width=5)
        self.side_cb.grid(row=0, column=5, sticky="w", padx=6, pady=3)

        ttk.Label(r0, text="Variety:").grid(row=0, column=6, sticky="e", padx=6, pady=3)
        self.variety_var = tk.StringVar()
        self.variety_cb = ttk.Combobox(r0, textvariable=self.variety_var, state="readonly", width=20)
        self.variety_cb.grid(row=0, column=7, sticky="w", padx=6, pady=3)

        ttk.Label(r0, text="Clone:").grid(row=0, column=8, sticky="e", padx=6, pady=3)
        self.clone_var = tk.StringVar()
        self.clone_cb = ttk.Combobox(r0, textvariable=self.clone_var, state="readonly", width=20)
        self.clone_cb.grid(row=0, column=9, sticky="w", padx=6, pady=3)

        ttk.Label(r0, text="Rootstock:").grid(row=0, column=10, sticky="e", padx=6, pady=3)
        self.rootstock_var = tk.StringVar()
        self.rootstock_cb = ttk.Combobox(r0, textvariable=self.rootstock_var,
                                         state="readonly", width=20)
        self.rootstock_cb.grid(row=0, column=11, sticky="w", padx=6, pady=3)

        ttk.Button(r0, text="\u27f3", width=3,
                   command=self._load_lookups).grid(row=0, column=12, padx=4)

        r1 = ttk.Frame(form)
        r1.pack(fill="x", padx=10, pady=(2, 8))

        def _le(label, col, width=8):
            ttk.Label(r1, text=label).grid(row=0, column=col, sticky="e", padx=6, pady=3)
            e = ttk.Entry(r1, width=width)
            e.grid(row=0, column=col + 1, sticky="w", padx=6, pady=3)
            return e

        self.year_entry    = _le("Plant Year:",     0, 6)
        self.rwidth_entry  = _le("Row W (m):",      2, 7)
        self.tspace_entry  = _le("Tree Sp (m):",    4, 7)
        self.tcount_entry  = _le("Tree Count:",     6, 7)
        self.rlength_entry = _le("Row L (m):",      8, 7)
        self.area_entry    = _le("Area (m\u00b2):", 10, 9)

        ttk.Label(r1, text="Notes:").grid(row=0, column=12, sticky="e", padx=6, pady=3)
        self.notes_entry = ttk.Entry(r1, width=26)
        self.notes_entry.grid(row=0, column=13, sticky="w", padx=6, pady=3)

        ttk.Button(r1, text="Save", command=self._save).grid(row=0, column=14, padx=12)

    def _build_filter(self):
        fbar = ttk.Frame(self)
        fbar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Label(fbar, text="Filter by Block:").pack(side="left", padx=(0, 6))
        self.filter_var = tk.StringVar(value="\u2014 All Blocks \u2014")
        self.filter_cb = ttk.Combobox(fbar, textvariable=self.filter_var,
                                      state="readonly", width=28)
        self.filter_cb.pack(side="left")
        self.filter_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(6, 0))
        ttk.Button(bar, text="\u27f3  Refresh",          command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\u270e  Edit Selected",     command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\U0001f5d1  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ["id", "block", "row_number", "side", "variety", "clone",
                "rootstock", "plant_year", "row_w", "tree_sp",
                "trees", "row_l", "area_m2", "notes", "created_at", "updated_at"]
        widths = {
            "id": 80, "block": 130, "row_number": 58, "side": 44,
            "variety": 140, "clone": 140, "rootstock": 130,
            "plant_year": 72, "row_w": 64, "tree_sp": 68,
            "trees": 58, "row_l": 64, "area_m2": 74,
            "notes": 180, "created_at": 128, "updated_at": 128,
        }
        self.tree = build_tree(self, cols, widths)

    def _load_lookups(self):
        try:
            self._block_map   = {b["name"]: b["id"] for b in api.get_blocks()}
            self._variety_map = {v["name"]: v["id"] for v in api.get_varieties()}
            self._clone_map   = {c["name"]: c["id"] for c in api.get_variety_clones()}
            self._rootstock_map = {"\u2014 None \u2014": None}
            self._rootstock_map.update({r["name"]: r["id"] for r in api.get_rootstocks()})
        except Exception as e:
            messagebox.showerror("Error loading lookups", str(e), parent=_top(self))

        self.block_cb["values"] = list(self._block_map.keys())
        if self._block_map:
            self.block_cb.current(0)

        self.variety_cb["values"] = list(self._variety_map.keys())
        if self._variety_map:
            self.variety_cb.current(0)

        self.clone_cb["values"] = [""] + list(self._clone_map.keys())
        self.clone_cb.current(0)

        self.rootstock_cb["values"] = list(self._rootstock_map.keys())
        self.rootstock_cb.current(0)

        all_lbl = "\u2014 All Blocks \u2014"
        choices = [all_lbl] + list(self._block_map.keys())
        current = self.filter_var.get()
        self.filter_cb["values"] = choices
        if current not in choices:
            self.filter_var.set(all_lbl)

    def _apply_filter(self):
        try:
            rows = api.get_block_rows()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))
            return
        self._draw_rows(rows)

    def refresh(self):
        self._load_lookups()
        try:
            rows = api.get_block_rows()
        except RuntimeError as e:
            messagebox.showerror("API Error",
                f"Could not load block rows.\n\n{e}\n\n"
                "Make sure the API server has been restarted and "
                "'alembic upgrade head' has been run.",
                parent=_top(self))
            return
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))
            return
        self._draw_rows(rows)

    def _draw_rows(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        all_lbl   = "\u2014 All Blocks \u2014"
        selected  = self.filter_var.get()
        filter_id = None if selected == all_lbl else self._block_map.get(selected)

        blk_lkp = {v: k for k, v in self._block_map.items()}
        var_lkp = {v: k for k, v in self._variety_map.items()}
        cln_lkp = {v: k for k, v in self._clone_map.items()}
        rs_lkp  = {v: k for k, v in self._rootstock_map.items() if v is not None}

        for r in rows:
            if filter_id and r["block_id"] != filter_id:
                continue
            self.tree.insert("", "end", iid=r["id"], values=(
                r["id"][:8] + "\u2026",
                blk_lkp.get(r["block_id"], "?"),
                r["row_number"],
                r["side"],
                var_lkp.get(r["variety_id"], "?"),
                cln_lkp.get(r["clone_id"], "?"),
                rs_lkp.get(r["rootstock_id"], "") if r["rootstock_id"] else "",
                r["planting_year"] or "",
                r["row_width_m"] or "",
                r["tree_spacing_m"] or "",
                r["tree_count"] or "",
                r["row_length_m"] or "",
                r["area_m2"] or "",
                r["notes"] or "",
                (r["created_at"] or "")[:16],
                (r["updated_at"] or "")[:16],
            ))

    def _collect_form(self):
        block_id     = self._block_map.get(self.block_var.get())
        variety_id   = self._variety_map.get(self.variety_var.get())
        clone_id     = self._clone_map.get(self.clone_var.get())
        rootstock_id = self._rootstock_map.get(self.rootstock_var.get())
        side         = self.side_var.get() or None   # empty selection → NULL

        if not block_id:
            messagebox.showerror("Validation", "Please select a Block.", parent=_top(self))
            return None
        if not variety_id:
            messagebox.showerror("Validation", "Please select a Variety.", parent=_top(self))
            return None
        try:
            row_number = int(self.row_num_entry.get().strip())
        except ValueError:
            messagebox.showerror("Validation", "Row # must be an integer.", parent=_top(self))
            return None

        def _oi(e):
            v = e.get().strip(); return int(v) if v else None
        def _od(e):
            v = e.get().strip(); return v if v else None

        return {
            "block_id":       str(block_id),
            "row_number":     row_number,
            "side":           side,
            "variety_id":     str(variety_id),
            "clone_id":       str(clone_id) if clone_id else None,
            "rootstock_id":   str(rootstock_id) if rootstock_id else None,
            "planting_year":  _oi(self.year_entry),
            "row_width_m":    _od(self.rwidth_entry),
            "tree_spacing_m": _od(self.tspace_entry),
            "tree_count":     _oi(self.tcount_entry),
            "row_length_m":   _od(self.rlength_entry),
            "area_m2":        _od(self.area_entry),
            "notes":          self.notes_entry.get().strip() or None,
        }

    def _save(self):
        payload = self._collect_form()
        if payload is None:
            return
        try:
            api.create_block_row(payload)
            for e in (self.row_num_entry, self.year_entry, self.rwidth_entry,
                      self.tspace_entry, self.tcount_entry, self.rlength_entry,
                      self.area_entry, self.notes_entry):
                e.delete(0, tk.END)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select a row", "Please select a record first.", parent=_top(self))
            return None
        return sel[0]

    def _edit(self):
        iid = self._selected_id()
        if not iid:
            return
        row = next((r for r in api.get_block_rows() if r["id"] == iid), None)
        if not row:
            return

        dlg = EditDialog(_top(self), "Edit Block Row", {
            "Row #":            str(row["row_number"]),
            "Side (N/S/E/W)":   row["side"],
            "Planting Year":    str(row["planting_year"] or ""),
            "Row Width (m)":    str(row["row_width_m"] or ""),
            "Tree Spacing (m)": str(row["tree_spacing_m"] or ""),
            "Tree Count":       str(row["tree_count"] or ""),
            "Row Length (m)":   str(row["row_length_m"] or ""),
            "Area (m\u00b2)":   str(row["area_m2"] or ""),
            "Notes":            row["notes"] or "",
        })
        if dlg.result is None:
            return

        side = dlg.result["Side (N/S/E/W)"].strip().upper() or None
        if side is not None and side not in SIDES:
            messagebox.showerror("Validation", "Side must be N, S, E, W or blank.", parent=_top(self))
            return

        def _oi(k):
            v = dlg.result[k].strip(); return int(v) if v else None
        def _od(k):
            v = dlg.result[k].strip(); return v if v else None

        payload = {k: v for k, v in {
            "row_number":     _oi("Row #"),
            "side":           side,
            "planting_year":  _oi("Planting Year"),
            "row_width_m":    _od("Row Width (m)"),
            "tree_spacing_m": _od("Tree Spacing (m)"),
            "tree_count":     _oi("Tree Count"),
            "row_length_m":   _od("Row Length (m)"),
            "area_m2":        _od("Area (m\u00b2)"),
            "notes":          dlg.result["Notes"] or None,
        }.items() if v is not None}

        try:
            api.update_block_row(iid, payload)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _delete(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   "Permanently delete this block row?", parent=_top(self)):
            return
        try:
            api.delete_block_row(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))


class FieldManagementWindow(tk.Toplevel):
    """Field Management UI — launched from the Santa Rita Control Panel."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Field Management")
        self.configure(bg="#f4f1ea")
        self.resizable(True, True)
        self.minsize(1100, 600)

        _apply_style(self)
        _maximize(self)
        _build_header(self, "Field Management",
                      "Santa Rita Farm  •  Manage farm fields")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        notebook.add(FieldsTab(notebook),    text="  Fields  ")
        notebook.add(BlocksTab(notebook),    text="  Blocks  ")
        notebook.add(BlockRowsTab(notebook), text="  Block Rows  ")

        self.grab_set()

