"""
Organisation Management GUI
Manages the Businesses and Sites database tables.
Launched from the Santa Rita Control Panel.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import app.api_client as api

# ─────────────────────────────────────────────
# Re-use the same palette / helpers from gui.py
# ─────────────────────────────────────────────

BG_MAIN       = "#f4f1ea"
BG_HEADER     = "#1b3a1b"
BG_CARD       = "#ffffff"
FG_HEADER     = "#ffffff"
FG_SUBTITLE   = "#a8c8a0"
FG_TITLE      = "#ffffff"
FG_LABEL      = "#1b3a1b"
ACCENT        = "#2e6b2e"
ACCENT_DARK   = "#174f17"
BORDER        = "#c8dfc8"


def _apply_style(root: tk.Misc):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG_MAIN, foreground=FG_LABEL,
                    font=("Helvetica", 10))
    style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
    style.configure("TNotebook.Tab", background=BG_CARD, foreground=FG_LABEL,
                    padding=[14, 6], font=("Helvetica", 10, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", FG_HEADER)])
    style.configure("TFrame",      background=BG_MAIN)
    style.configure("TLabelframe", background=BG_MAIN, foreground=ACCENT,
                    bordercolor=BORDER, font=("Helvetica", 10, "bold"))
    style.configure("TLabelframe.Label", background=BG_MAIN, foreground=ACCENT,
                    font=("Helvetica", 10, "bold"))
    style.configure("TLabel", background=BG_MAIN, foreground=FG_LABEL,
                    font=("Helvetica", 10))
    style.configure("TEntry", fieldbackground=BG_CARD, foreground=FG_LABEL,
                    insertcolor=FG_LABEL, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER)
    style.configure("TCombobox", fieldbackground=BG_CARD, foreground=FG_LABEL,
                    background=BG_CARD, bordercolor=BORDER, arrowcolor=ACCENT)
    style.configure("TButton", background=ACCENT, foreground=FG_HEADER,
                    font=("Helvetica", 10, "bold"), borderwidth=0,
                    focusthickness=0, padding=[10, 5])
    style.map("TButton",
              background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
              foreground=[("active", FG_HEADER)])
    style.configure("Treeview", background=BG_CARD, foreground=FG_LABEL,
                    fieldbackground=BG_CARD, rowheight=26, borderwidth=0,
                    font=("Helvetica", 10))
    style.configure("Treeview.Heading", background=ACCENT, foreground=FG_HEADER,
                    font=("Helvetica", 10, "bold"), relief="flat")
    style.map("Treeview",
              background=[("selected", BG_HEADER)],
              foreground=[("selected", FG_HEADER)])
    style.map("Treeview.Heading",
              background=[("active", ACCENT_DARK)])
    style.configure("TScrollbar", background=BORDER, troughcolor=BG_MAIN,
                    arrowcolor=ACCENT)


def _maximize(window: tk.Misc):
    ws = window.tk.call("tk", "windowingsystem")
    if ws == "win32":
        window.state("zoomed")
    elif ws == "x11":
        window.attributes("-zoomed", True)
    else:
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry(f"{w}x{h}+0+0")


def _build_header(window: tk.Misc, title: str, subtitle: str = ""):
    header = tk.Frame(window, bg=BG_HEADER)
    header.pack(fill="x")

    tk.Label(header, text="🌿", font=("Helvetica", 22),
             bg=BG_HEADER, fg=FG_SUBTITLE).pack(side="left", padx=(18, 8), pady=12)

    text_frame = tk.Frame(header, bg=BG_HEADER)
    text_frame.pack(side="left", pady=8)
    tk.Label(text_frame, text=title, font=("Helvetica", 16, "bold"),
             bg=BG_HEADER, fg=FG_TITLE).pack(anchor="w")
    if subtitle:
        tk.Label(text_frame, text=subtitle, font=("Helvetica", 9),
                 bg=BG_HEADER, fg=FG_SUBTITLE).pack(anchor="w")


def _top(widget) -> tk.Misc:
    return widget.winfo_toplevel()


# ─────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────

def build_tree(parent, cols: list, widths: dict = None) -> ttk.Treeview:
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=8)

    tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
    for col in cols:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=(widths or {}).get(col, 130))

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return tree


class EditDialog(tk.Toplevel):
    """Generic dialog for editing a set of named text fields."""

    def __init__(self, parent, title: str, fields: dict):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        _apply_style(self)
        _build_header(self, title)

        inner = ttk.Frame(self)
        inner.pack(padx=20, pady=16)

        self._entries = {}
        for row, (label, value) in enumerate(fields.items()):
            ttk.Label(inner, text=label + ":").grid(row=row, column=0, sticky="e", padx=10, pady=6)
            e = ttk.Entry(inner, width=36)
            e.insert(0, str(value) if value is not None else "")
            e.grid(row=row, column=1, sticky="w", padx=10, pady=6)
            self._entries[label] = e

        btn_frame = ttk.Frame(inner)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="Save",   command=self._ok).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=6)

        self.wait_window()

    def _ok(self):
        self.result = {label: e.get().strip() for label, e in self._entries.items()}
        self.destroy()


# ─────────────────────────────────────────────
# Businesses Tab
# ─────────────────────────────────────────────

class BusinessesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Business")
        form.pack(fill="x", padx=10, pady=(12, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=10)

        ttk.Label(fields, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_entry = ttk.Entry(fields, width=28)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="Code (optional):").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.code_entry = ttk.Entry(fields, width=16)
        self.code_entry.grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Button(fields, text="Save", command=self._save).grid(row=0, column=4, padx=12)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="⟳  Refresh",      command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎  Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="🗑  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ("id", "name", "code", "created_at", "updated_at")
        self.tree = build_tree(self, cols, {"id": 90, "name": 200, "code": 120,
                                            "created_at": 160, "updated_at": 160})

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            for b in api.get_businesses():
                self.tree.insert("", "end", iid=b["id"], values=(
                    b["id"][:8] + "…",
                    b["name"],
                    b["code"] or "",
                    (b["created_at"] or "")[:16],
                    (b["updated_at"] or "")[:16],
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _save(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip() or None
        if not name:
            messagebox.showerror("Validation", "Name is required.", parent=_top(self))
            return
        try:
            api.create_business(name, code)
            self.name_entry.delete(0, tk.END)
            self.code_entry.delete(0, tk.END)
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
        row = next((b for b in api.get_businesses() if b["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(_top(self), "Edit Business", {
            "Name": row["name"],
            "Code": row["code"] or "",
        })
        if dlg.result is None:
            return
        try:
            api.update_business(iid, dlg.result["Name"], dlg.result["Code"] or None)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _delete(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   "Permanently delete this business?", parent=_top(self)):
            return
        try:
            api.delete_business(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))


# ─────────────────────────────────────────────
# Sites Tab
# ─────────────────────────────────────────────

class SitesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._business_map = {}   # label -> business_id
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Site")
        form.pack(fill="x", padx=10, pady=(12, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=10)

        # Row 0
        ttk.Label(fields, text="Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.name_entry = ttk.Entry(fields, width=22)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="Code (optional):").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.code_entry = ttk.Entry(fields, width=14)
        self.code_entry.grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="Type:").grid(row=0, column=4, sticky="e", padx=6, pady=4)
        self.type_entry = ttk.Entry(fields, width=16)
        self.type_entry.grid(row=0, column=5, sticky="w", padx=6, pady=4)

        # Row 1
        ttk.Label(fields, text="Business:").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.business_var = tk.StringVar()
        self.business_cb = ttk.Combobox(fields, textvariable=self.business_var,
                                        state="readonly", width=24)
        self.business_cb.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        ttk.Button(fields, text="⟳", width=3,
                   command=self._load_businesses).grid(row=1, column=2, padx=2)

        ttk.Label(fields, text="Address:").grid(row=1, column=3, sticky="e", padx=6, pady=4)
        self.address_entry = ttk.Entry(fields, width=28)
        self.address_entry.grid(row=1, column=4, columnspan=2, sticky="w", padx=6, pady=4)

        # Row 2
        ttk.Label(fields, text="Notes (optional):").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        self.notes_entry = ttk.Entry(fields, width=48)
        self.notes_entry.grid(row=2, column=1, columnspan=5, sticky="w", padx=6, pady=4)

        ttk.Button(fields, text="Save", command=self._save).grid(row=2, column=6, padx=12)

        self._load_businesses()

    def _load_businesses(self):
        self._business_map.clear()
        # Add a blank option so user can leave FK empty
        self._business_map["— None —"] = None
        try:
            for b in api.get_businesses():
                label = f"{b['name']} ({b['id'][:8]}…)"
                self._business_map[label] = b["id"]
        except Exception as e:
            messagebox.showerror("Error loading businesses", str(e), parent=_top(self))
        self.business_cb["values"] = list(self._business_map.keys())
        self.business_cb.current(0)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="⟳  Refresh",      command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎  Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="🗑  Delete Record", command=self._delete).pack(side="left")

    def _build_tree(self):
        cols = ("id", "name", "code", "business", "type", "address", "notes",
                "created_at", "updated_at")
        self.tree = build_tree(self, cols,
                               {"id": 90, "name": 160, "code": 100, "business": 160,
                                "type": 100, "address": 180, "notes": 180,
                                "created_at": 150, "updated_at": 150})

    def refresh(self):
        self._load_businesses()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            biz_lookup = {b["id"]: b["name"] for b in api.get_businesses()}
            for s in api.get_sites():
                biz_name = biz_lookup.get(s.get("business_id"), "") if s.get("business_id") else ""
                self.tree.insert("", "end", iid=s["id"], values=(
                    s["id"][:8] + "…",
                    s["name"],
                    s["code"] or "",
                    biz_name,
                    s["type"],
                    s["address"] or "",
                    s["notes"] or "",
                    (s["created_at"] or "")[:16],
                    (s["updated_at"] or "")[:16],
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))

    def _save(self):
        name    = self.name_entry.get().strip()
        code    = self.code_entry.get().strip() or None
        type_   = self.type_entry.get().strip()
        address = self.address_entry.get().strip()
        notes   = self.notes_entry.get().strip() or None
        biz_label = self.business_var.get()
        business_id = self._business_map.get(biz_label)  # may be None

        if not name or not type_ or not address:
            messagebox.showerror("Validation",
                                 "Name, Type and Address are required.", parent=_top(self))
            return
        try:
            api.create_site(name, code, business_id, type_, address, notes)
            for widget in (self.name_entry, self.code_entry,
                           self.type_entry, self.address_entry, self.notes_entry):
                widget.delete(0, tk.END)
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
        row = next((s for s in api.get_sites() if s["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(_top(self), "Edit Site", {
            "Name":    row["name"],
            "Code":    row["code"] or "",
            "Type":    row["type"],
            "Address": row["address"] or "",
            "Notes":   row["notes"] or "",
        })
        if dlg.result is None:
            return
        try:
            api.update_site(
                iid,
                dlg.result["Name"],
                dlg.result["Code"] or None,
                dlg.result["Type"],
                dlg.result["Address"],
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
                                   "Permanently delete this site?", parent=_top(self)):
            return
        try:
            api.delete_site(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=_top(self))


# ─────────────────────────────────────────────
# Organisation Management window
# ─────────────────────────────────────────────

def _build_notebook(window: tk.Misc):
    notebook = ttk.Notebook(window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    businesses_tab = BusinessesTab(notebook)
    sites_tab      = SitesTab(notebook)

    notebook.add(businesses_tab, text="  Businesses  ")
    notebook.add(sites_tab,      text="  Sites  ")

    return notebook


class OrgManagementWindow(tk.Toplevel):
    """Organisation Management UI — launched from the Santa Rita Control Panel."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Organisation Management")
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)
        self.minsize(1100, 600)

        _apply_style(self)
        _maximize(self)
        _build_header(self, "Organisation Management",
                      "Santa Rita Farm  •  Manage businesses & sites")
        _build_notebook(self)

        self.grab_set()

