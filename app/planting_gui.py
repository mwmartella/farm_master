"""
Planting Material Manager GUI
Launched from the Santa Rita Control Panel.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import app.api_client as api
from app.org_gui import _apply_style, _maximize, _build_header, build_tree, EditDialog, _top


class FruitTypesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Fruit Type")
        form.pack(fill="x", padx=10, pady=(12, 0))
        f = ttk.Frame(form)
        f.pack(side="left", padx=10, pady=10)
        ttk.Label(f, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_entry = ttk.Entry(f, width=28)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(f, text="Notes (optional):").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.notes_entry = ttk.Entry(f, width=40)
        self.notes_entry.grid(row=0, column=3, sticky="w", padx=6, pady=4)
        ttk.Button(f, text="Save", command=self._save).grid(row=0, column=4, padx=12)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="⟳  Refresh",      command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎  Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="🗑  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ["id", "name", "notes", "created_at", "updated_at"]
        self.tree = build_tree(self, cols, {"id": 90, "name": 200, "notes": 300, "created_at": 160, "updated_at": 160})

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            for ft in api.get_fruit_types():
                self.tree.insert("", "end", iid=ft["id"], values=(
                    ft["id"][:8] + "…", ft["name"], ft["notes"] or "",
                    (ft["created_at"] or "")[:16], (ft["updated_at"] or "")[:16],
                ))
        except RuntimeError as e:
            messagebox.showerror("API Error",
                f"Could not load fruit types.\n\n{e}\n\nMake sure the API server has been restarted and 'alembic upgrade head' has been run on the server.",
                parent=_top(self))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _save(self):
        name  = self.name_entry.get().strip()
        notes = self.notes_entry.get().strip() or None
        if not name:
            messagebox.showerror("Validation", "Name is required.", parent=_top(self))
            return
        try:
            api.create_fruit_type(name, notes)
            self.name_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
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
        row = next((ft for ft in api.get_fruit_types() if ft["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(_top(self), "Edit Fruit Type", {"Name": row["name"], "Notes": row["notes"] or ""})
        if dlg.result is None:
            return
        try:
            api.update_fruit_type(iid, dlg.result["Name"], dlg.result["Notes"] or None)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _delete(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm Delete", "Permanently delete this fruit type?", parent=_top(self)):
            return
        try:
            api.delete_fruit_type(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))




# ─────────────────────────────────────────────
# Varieties Tab
# ─────────────────────────────────────────────

class VarietiesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._fruit_type_map = {}  # label -> fruit_type_id
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Variety")
        form.pack(fill="x", padx=10, pady=(12, 0))
        f = ttk.Frame(form)
        f.pack(side="left", padx=10, pady=10)

        ttk.Label(f, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_entry = ttk.Entry(f, width=28)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Fruit Type:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.fruit_type_var = tk.StringVar()
        self.fruit_type_cb = ttk.Combobox(f, textvariable=self.fruit_type_var,
                                          state="readonly", width=26)
        self.fruit_type_cb.grid(row=0, column=3, sticky="w", padx=6, pady=4)
        ttk.Button(f, text="\u27f3", width=3,
                   command=self._load_fruit_types).grid(row=0, column=4, padx=2)

        ttk.Button(f, text="Save", command=self._save).grid(row=0, column=5, padx=12)

        self._load_fruit_types()

    def _load_fruit_types(self):
        self._fruit_type_map.clear()
        try:
            for ft in api.get_fruit_types():
                self._fruit_type_map[ft["name"]] = ft["id"]
        except Exception as e:
            messagebox.showerror("Error loading fruit types", str(e), parent=_top(self))
        self.fruit_type_cb["values"] = list(self._fruit_type_map.keys())
        if self._fruit_type_map:
            self.fruit_type_cb.current(0)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="\u27f3  Refresh",      command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\u270e  Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\U0001f5d1  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ["id", "name", "fruit_type", "created_at", "updated_at"]
        self.tree = build_tree(self, cols,
                               {"id": 90, "name": 220, "fruit_type": 200,
                                "created_at": 160, "updated_at": 160})

    def refresh(self):
        self._load_fruit_types()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            ft_lookup = {ft["id"]: ft["name"] for ft in api.get_fruit_types()}
            for v in api.get_varieties():
                self.tree.insert("", "end", iid=v["id"], values=(
                    v["id"][:8] + "\u2026",
                    v["name"],
                    ft_lookup.get(v["fruit_type_id"], "Unknown"),
                    (v["created_at"] or "")[:16],
                    (v["updated_at"] or "")[:16],
                ))
        except RuntimeError as e:
            messagebox.showerror("API Error",
                f"Could not load varieties.\n\n{e}\n\n"
                "Make sure the API server has been restarted and "
                "'alembic upgrade head' has been run on the server.",
                parent=_top(self))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _save(self):
        name = self.name_entry.get().strip()
        ft_label = self.fruit_type_var.get()
        fruit_type_id = self._fruit_type_map.get(ft_label)
        if not name:
            messagebox.showerror("Validation", "Name is required.", parent=_top(self))
            return
        if not fruit_type_id:
            messagebox.showerror("Validation", "Please select a Fruit Type.", parent=_top(self))
            return
        try:
            api.create_variety(name, fruit_type_id)
            self.name_entry.delete(0, tk.END)
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
        row = next((v for v in api.get_varieties() if v["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(_top(self), "Edit Variety", {"Name": row["name"]})
        if dlg.result is None:
            return
        try:
            api.update_variety(iid, dlg.result["Name"])
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _delete(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   "Permanently delete this variety?", parent=_top(self)):
            return
        try:
            api.delete_variety(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))




# ─────────────────────────────────────────────
# Variety Clones Tab
# ─────────────────────────────────────────────

class VarietyClonesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._variety_map = {}   # label -> variety_id
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Variety Clone")
        form.pack(fill="x", padx=10, pady=(12, 0))
        f = ttk.Frame(form)
        f.pack(side="left", padx=10, pady=10)

        ttk.Label(f, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_entry = ttk.Entry(f, width=28)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Variety:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.variety_var = tk.StringVar()
        self.variety_cb = ttk.Combobox(f, textvariable=self.variety_var,
                                       state="readonly", width=26)
        self.variety_cb.grid(row=0, column=3, sticky="w", padx=6, pady=4)
        ttk.Button(f, text="\u27f3", width=3,
                   command=self._load_varieties).grid(row=0, column=4, padx=2)

        ttk.Label(f, text="Notes (optional):").grid(row=0, column=5, sticky="e", padx=6, pady=4)
        self.notes_entry = ttk.Entry(f, width=28)
        self.notes_entry.grid(row=0, column=6, sticky="w", padx=6, pady=4)

        ttk.Button(f, text="Save", command=self._save).grid(row=0, column=7, padx=12)

        self._load_varieties()

    def _load_varieties(self):
        self._variety_map.clear()
        try:
            for v in api.get_varieties():
                self._variety_map[v["name"]] = v["id"]
        except Exception as e:
            messagebox.showerror("Error loading varieties", str(e), parent=_top(self))
        self.variety_cb["values"] = list(self._variety_map.keys())
        if self._variety_map:
            self.variety_cb.current(0)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="\u27f3  Refresh",       command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\u270e  Edit Selected",  command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\U0001f5d1  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ["id", "name", "variety", "notes", "created_at", "updated_at"]
        self.tree = build_tree(self, cols,
                               {"id": 90, "name": 200, "variety": 200,
                                "notes": 220, "created_at": 150, "updated_at": 150})

    def refresh(self):
        self._load_varieties()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            variety_lookup = {v["id"]: v["name"] for v in api.get_varieties()}
            for vc in api.get_variety_clones():
                self.tree.insert("", "end", iid=vc["id"], values=(
                    vc["id"][:8] + "\u2026",
                    vc["name"],
                    variety_lookup.get(vc["variety_id"], "Unknown"),
                    vc["notes"] or "",
                    (vc["created_at"] or "")[:16],
                    (vc["updated_at"] or "")[:16],
                ))
        except RuntimeError as e:
            messagebox.showerror("API Error",
                f"Could not load variety clones.\n\n{e}\n\n"
                "Make sure the API server has been restarted and "
                "'alembic upgrade head' has been run on the server.",
                parent=_top(self))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _save(self):
        name      = self.name_entry.get().strip()
        variety_id = self._variety_map.get(self.variety_var.get())
        notes     = self.notes_entry.get().strip() or None
        if not name:
            messagebox.showerror("Validation", "Name is required.", parent=_top(self))
            return
        if not variety_id:
            messagebox.showerror("Validation", "Please select a Variety.", parent=_top(self))
            return
        try:
            api.create_variety_clone(name, variety_id, notes)
            self.name_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
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
        row = next((vc for vc in api.get_variety_clones() if vc["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(_top(self), "Edit Variety Clone", {
            "Name":  row["name"],
            "Notes": row["notes"] or "",
        })
        if dlg.result is None:
            return
        try:
            api.update_variety_clone(iid, dlg.result["Name"], dlg.result["Notes"] or None)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _delete(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   "Permanently delete this variety clone?", parent=_top(self)):
            return
        try:
            api.delete_variety_clone(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))


class PlantingMaterialWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Planting Material Manager")
        self.configure(bg="#f4f1ea")
        self.resizable(True, True)
        self.minsize(960, 560)
        _apply_style(self)
        _maximize(self)
        _build_header(self, "Planting Material Manager",
                      "Santa Rita Farm  •  Manage fruit types and planting material")
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        notebook.add(FruitTypesTab(notebook),    text="  Fruit Types  ")
        notebook.add(VarietiesTab(notebook),     text="  Varieties  ")
        notebook.add(VarietyClonesTab(notebook), text="  Variety Clones  ")
        notebook.add(RootstocksTab(notebook),    text="  Rootstocks  ")
        self.grab_set()


class RootstocksTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._fruit_type_map = {}   # label -> fruit_type_id
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Rootstock")
        form.pack(fill="x", padx=10, pady=(12, 0))
        f = ttk.Frame(form)
        f.pack(side="left", padx=10, pady=10)

        ttk.Label(f, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_entry = ttk.Entry(f, width=24)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Fruit Type:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.fruit_type_var = tk.StringVar()
        self.fruit_type_cb = ttk.Combobox(f, textvariable=self.fruit_type_var,
                                          state="readonly", width=22)
        self.fruit_type_cb.grid(row=0, column=3, sticky="w", padx=6, pady=4)
        ttk.Button(f, text="\u27f3", width=3,
                   command=self._load_fruit_types).grid(row=0, column=4, padx=2)

        ttk.Label(f, text="Vigour Class:").grid(row=0, column=5, sticky="e", padx=6, pady=4)
        self.vigour_entry = ttk.Entry(f, width=16)
        self.vigour_entry.grid(row=0, column=6, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Notes (optional):").grid(row=0, column=7, sticky="e", padx=6, pady=4)
        self.notes_entry = ttk.Entry(f, width=28)
        self.notes_entry.grid(row=0, column=8, sticky="w", padx=6, pady=4)

        ttk.Button(f, text="Save", command=self._save).grid(row=0, column=9, padx=12)

        self._load_fruit_types()

    def _load_fruit_types(self):
        self._fruit_type_map.clear()
        try:
            for ft in api.get_fruit_types():
                self._fruit_type_map[ft["name"]] = ft["id"]
        except Exception as e:
            messagebox.showerror("Error loading fruit types", str(e), parent=_top(self))
        self.fruit_type_cb["values"] = list(self._fruit_type_map.keys())
        if self._fruit_type_map:
            self.fruit_type_cb.current(0)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="\u27f3  Refresh",        command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\u270e  Edit Selected",   command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\U0001f5d1  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ["id", "name", "fruit_type", "vigour_class", "notes", "created_at", "updated_at"]
        self.tree = build_tree(self, cols,
                               {"id": 90, "name": 180, "fruit_type": 160,
                                "vigour_class": 120, "notes": 220,
                                "created_at": 140, "updated_at": 140})

    def refresh(self):
        self._load_fruit_types()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            ft_lookup = {v: k for k, v in self._fruit_type_map.items()}
            for rs in api.get_rootstocks():
                self.tree.insert("", "end", iid=rs["id"], values=(
                    rs["id"][:8] + "\u2026",
                    rs["name"],
                    ft_lookup.get(rs["fruit_type_id"], "Unknown"),
                    rs["vigour_class"] or "",
                    rs["notes"] or "",
                    (rs["created_at"] or "")[:16],
                    (rs["updated_at"] or "")[:16],
                ))
        except RuntimeError as e:
            messagebox.showerror("API Error",
                f"Could not load rootstocks.\n\n{e}\n\n"
                "Make sure the API server has been restarted and "
                "'alembic upgrade head' has been run.",
                parent=_top(self))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _save(self):
        name         = self.name_entry.get().strip()
        fruit_type_id = self._fruit_type_map.get(self.fruit_type_var.get())
        vigour_class  = self.vigour_entry.get().strip() or None
        notes         = self.notes_entry.get().strip() or None
        if not name:
            messagebox.showerror("Validation", "Name is required.", parent=_top(self))
            return
        if not fruit_type_id:
            messagebox.showerror("Validation", "Please select a Fruit Type.", parent=_top(self))
            return
        try:
            api.create_rootstock(name, fruit_type_id, vigour_class, notes)
            for entry in (self.name_entry, self.vigour_entry, self.notes_entry):
                entry.delete(0, tk.END)
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
        row = next((rs for rs in api.get_rootstocks() if rs["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(_top(self), "Edit Rootstock", {
            "Name":         row["name"],
            "Vigour Class": row["vigour_class"] or "",
            "Notes":        row["notes"] or "",
        })
        if dlg.result is None:
            return
        try:
            api.update_rootstock(
                iid,
                dlg.result["Name"],
                dlg.result["Vigour Class"] or None,
                dlg.result["Notes"] or None,
            )
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _delete(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   "Permanently delete this rootstock?", parent=_top(self)):
            return
        try:
            api.delete_rootstock(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))


class BlocksTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._field_map = {}   # label -> field_id
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Block")
        form.pack(fill="x", padx=10, pady=(12, 0))
        f = ttk.Frame(form)
        f.pack(side="left", padx=10, pady=10)

        ttk.Label(f, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_entry = ttk.Entry(f, width=22)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Field:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.field_var = tk.StringVar()
        self.field_cb = ttk.Combobox(f, textvariable=self.field_var,
                                     state="readonly", width=22)
        self.field_cb.grid(row=0, column=3, sticky="w", padx=6, pady=4)
        ttk.Button(f, text="\u27f3", width=3,
                   command=self._load_fields).grid(row=0, column=4, padx=2)

        ttk.Label(f, text="Code:").grid(row=0, column=5, sticky="e", padx=6, pady=4)
        self.code_entry = ttk.Entry(f, width=14)
        self.code_entry.grid(row=0, column=6, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Type:").grid(row=0, column=7, sticky="e", padx=6, pady=4)
        self.type_entry = ttk.Entry(f, width=14)
        self.type_entry.grid(row=0, column=8, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Notes:").grid(row=0, column=9, sticky="e", padx=6, pady=4)
        self.notes_entry = ttk.Entry(f, width=22)
        self.notes_entry.grid(row=0, column=10, sticky="w", padx=6, pady=4)

        ttk.Button(f, text="Save", command=self._save).grid(row=0, column=11, padx=12)

        self._load_fields()

    def _load_fields(self):
        self._field_map.clear()
        try:
            for field in api.get_fields():
                self._field_map[field["name"]] = field["id"]
        except Exception as e:
            messagebox.showerror("Error loading fields", str(e), parent=_top(self))
        self.field_cb["values"] = list(self._field_map.keys())
        if self._field_map:
            self.field_cb.current(0)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="\u27f3  Refresh",        command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\u270e  Edit Selected",   command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="\U0001f5d1  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ["id", "name", "field", "code", "block_type", "notes", "created_at", "updated_at"]
        self.tree = build_tree(self, cols,
                               {"id": 90, "name": 160, "field": 160, "code": 90,
                                "block_type": 110, "notes": 200,
                                "created_at": 140, "updated_at": 140})

    def refresh(self):
        self._load_fields()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            field_lookup = {v: k for k, v in self._field_map.items()}
            for b in api.get_blocks():
                self.tree.insert("", "end", iid=b["id"], values=(
                    b["id"][:8] + "\u2026",
                    b["name"],
                    field_lookup.get(b["field_id"], "Unknown"),
                    b["code"] or "",
                    b["block_type"] or "",
                    b["notes"] or "",
                    (b["created_at"] or "")[:16],
                    (b["updated_at"] or "")[:16],
                ))
        except RuntimeError as e:
            messagebox.showerror("API Error",
                f"Could not load blocks.\n\n{e}\n\n"
                "Make sure the API server has been restarted and "
                "'alembic upgrade head' has been run.",
                parent=_top(self))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _save(self):
        name      = self.name_entry.get().strip()
        field_id  = self._field_map.get(self.field_var.get())
        code      = self.code_entry.get().strip() or None
        block_type = self.type_entry.get().strip() or None
        notes     = self.notes_entry.get().strip() or None
        if not name:
            messagebox.showerror("Validation", "Name is required.", parent=_top(self))
            return
        if not field_id:
            messagebox.showerror("Validation", "Please select a Field.", parent=_top(self))
            return
        try:
            api.create_block(field_id, name, code, block_type, notes)
            for entry in (self.name_entry, self.code_entry, self.type_entry, self.notes_entry):
                entry.delete(0, tk.END)
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
        row = next((b for b in api.get_blocks() if b["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(_top(self), "Edit Block", {
            "Name":       row["name"],
            "Code":       row["code"] or "",
            "Block Type": row["block_type"] or "",
            "Notes":      row["notes"] or "",
        })
        if dlg.result is None:
            return
        try:
            api.update_block(
                iid,
                dlg.result["Name"],
                dlg.result["Code"] or None,
                dlg.result["Block Type"] or None,
                dlg.result["Notes"] or None,
            )
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _delete(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   "Permanently delete this block?", parent=_top(self)):
            return
        try:
            api.delete_block(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

