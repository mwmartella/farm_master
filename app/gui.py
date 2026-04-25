import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import app.api_client as api

# ─────────────────────────────────────────────
# Colour / style constants  (mirrors control_panel.py)
# ─────────────────────────────────────────────

BG_MAIN       = "#f4f1ea"
BG_HEADER     = "#1b3a1b"
BG_CARD       = "#ffffff"
FG_HEADER     = "#ffffff"
FG_SUBTITLE   = "#a8c8a0"
FG_TITLE      = "#ffffff"
FG_LABEL      = "#1b3a1b"
FG_CARD_DESC  = "#555555"
ACCENT        = "#2e6b2e"
ACCENT_DARK   = "#174f17"
BORDER        = "#c8dfc8"


def _apply_style(root: tk.Misc):
    """Configure ttk styles to match the Santa Rita Control Panel palette."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
                    background=BG_MAIN,
                    foreground=FG_LABEL,
                    font=("Helvetica", 10))

    # Notebook
    style.configure("TNotebook",
                    background=BG_MAIN,
                    borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=BG_CARD,
                    foreground=FG_LABEL,
                    padding=[14, 6],
                    font=("Helvetica", 10, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", FG_HEADER)])

    # Frames & LabelFrames
    style.configure("TFrame",      background=BG_MAIN)
    style.configure("TLabelframe", background=BG_MAIN,
                    foreground=ACCENT, bordercolor=BORDER,
                    font=("Helvetica", 10, "bold"))
    style.configure("TLabelframe.Label", background=BG_MAIN,
                    foreground=ACCENT, font=("Helvetica", 10, "bold"))

    # Labels
    style.configure("TLabel",
                    background=BG_MAIN, foreground=FG_LABEL,
                    font=("Helvetica", 10))

    # Entries
    style.configure("TEntry",
                    fieldbackground=BG_CARD, foreground=FG_LABEL,
                    insertcolor=FG_LABEL, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER)

    # Combobox
    style.configure("TCombobox",
                    fieldbackground=BG_CARD, foreground=FG_LABEL,
                    background=BG_CARD, bordercolor=BORDER,
                    arrowcolor=ACCENT)

    # Buttons
    style.configure("TButton",
                    background=ACCENT, foreground=FG_HEADER,
                    font=("Helvetica", 10, "bold"),
                    borderwidth=0, focusthickness=0,
                    padding=[10, 5])
    style.map("TButton",
              background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
              foreground=[("active", FG_HEADER)])

    # Treeview
    style.configure("Treeview",
                    background=BG_CARD, foreground=FG_LABEL,
                    fieldbackground=BG_CARD,
                    rowheight=26, borderwidth=0,
                    font=("Helvetica", 10))
    style.configure("Treeview.Heading",
                    background=ACCENT, foreground=FG_HEADER,
                    font=("Helvetica", 10, "bold"),
                    relief="flat")
    style.map("Treeview",
              background=[("selected", BG_HEADER)],
              foreground=[("selected", FG_HEADER)])
    style.map("Treeview.Heading",
              background=[("active", ACCENT_DARK)])

    # Scrollbar
    style.configure("TScrollbar",
                    background=BORDER, troughcolor=BG_MAIN,
                    arrowcolor=ACCENT)


def _maximize(window: tk.Misc):
    """Maximize the window in a cross-platform way."""
    ws = window.tk.call("tk", "windowingsystem")
    if ws == "win32":
        window.state("zoomed")
    elif ws == "x11":
        window.attributes("-zoomed", True)
    else:  # aqua (macOS)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry(f"{w}x{h}+0+0")


def _build_header(window: tk.Misc, title: str, subtitle: str = ""):
    """Add a green header bar (same look as ControlPanel)."""
    header = tk.Frame(window, bg=BG_HEADER)
    header.pack(fill="x")

    tk.Label(header, text="🌿", font=("Helvetica", 22),
             bg=BG_HEADER, fg=FG_SUBTITLE).pack(side="left", padx=(18, 8), pady=12)

    text_frame = tk.Frame(header, bg=BG_HEADER)
    text_frame.pack(side="left", pady=8)
    tk.Label(text_frame, text=title,
             font=("Helvetica", 16, "bold"),
             bg=BG_HEADER, fg=FG_TITLE).pack(anchor="w")
    if subtitle:
        tk.Label(text_frame, text=subtitle,
                 font=("Helvetica", 9),
                 bg=BG_HEADER, fg=FG_SUBTITLE).pack(anchor="w")


# ─────────────────────────────────────────────
# Shared Edit Dialog
# ─────────────────────────────────────────────

class EditDialog(tk.Toplevel):
    """Generic dialog for editing a set of named fields."""

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
            e = ttk.Entry(inner, width=30)
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
# Shared Treeview builder
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


# ─────────────────────────────────────────────
# WorkerCodes Tab
# ─────────────────────────────────────────────

class WorkerCodesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Worker Code")
        form.pack(fill="x", padx=10, pady=(12, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=10)

        ttk.Label(fields, text="Code Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.code_name = ttk.Entry(fields, width=24)
        self.code_name.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="Description:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.code_desc = ttk.Entry(fields, width=32)
        self.code_desc.grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="Pay Rate:").grid(row=0, column=4, sticky="e", padx=6, pady=4)
        self.pay_rate = ttk.Entry(fields, width=10)
        self.pay_rate.grid(row=0, column=5, sticky="w", padx=6, pady=4)

        ttk.Button(fields, text="Save", command=self._save).grid(row=0, column=6, padx=12)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="⟳  Refresh",      command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎  Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="⏹  End Record",    command=self._end_record).pack(side="left")

    def _build_tree(self):
        cols = ("code_id", "code_name", "description", "pay_rate", "start_date", "end_date")
        self.tree = build_tree(self, cols, {"code_id": 90, "description": 200})

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            for wc in api.get_worker_codes():
                self.tree.insert("", "end", iid=wc["code_id"], values=(
                    wc["code_id"][:8] + "…",
                    wc["code_name"],
                    wc["code_description"],
                    wc["pay_rate"],
                    wc["start_date"][:16] if wc["start_date"] else "",
                    wc["end_date"][:16] if wc["end_date"] else "",
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save(self):
        try:
            name = self.code_name.get().strip()
            desc = self.code_desc.get().strip()
            rate = self.pay_rate.get().strip()
            if not name or not desc or not rate:
                messagebox.showerror("Validation", "All fields are required.")
                return
            api.create_worker_code(name, desc, rate)
            self.code_name.delete(0, tk.END)
            self.code_desc.delete(0, tk.END)
            self.pay_rate.delete(0, tk.END)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select a row", "Please select a record first.")
            return None
        return sel[0]

    def _edit(self):
        iid = self._selected_id()
        if not iid:
            return
        row = next((r for r in api.get_worker_codes() if r["code_id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(self, "Edit Worker Code", {
            "Code Name":   row["code_name"],
            "Description": row["code_description"],
            "Pay Rate":    row["pay_rate"],
        })
        if dlg.result is None:
            return
        try:
            api.update_worker_code(
                iid,
                dlg.result["Code Name"],
                dlg.result["Description"],
                dlg.result["Pay Rate"],
            )
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _end_record(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm", "Set end date to now for this record?"):
            return
        try:
            api.end_worker_code(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ─────────────────────────────────────────────
# Workers Tab
# ─────────────────────────────────────────────

class WorkersTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._code_map = {}
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Worker")
        form.pack(fill="x", padx=10, pady=(12, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=10)

        ttk.Label(fields, text="Worker Code:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.worker_code_var = tk.StringVar()
        self.worker_code_cb = ttk.Combobox(
            fields, textvariable=self.worker_code_var, state="readonly", width=26)
        self.worker_code_cb.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Button(fields, text="⟳", width=3,
                   command=self._load_codes).grid(row=0, column=2, padx=2)

        ttk.Label(fields, text="First Name:").grid(row=0, column=3, sticky="e", padx=6, pady=4)
        self.first_name = ttk.Entry(fields, width=18)
        self.first_name.grid(row=0, column=4, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="Last Name:").grid(row=0, column=5, sticky="e", padx=6, pady=4)
        self.last_name = ttk.Entry(fields, width=18)
        self.last_name.grid(row=0, column=6, sticky="w", padx=6, pady=4)

        ttk.Button(fields, text="Save", command=self._save).grid(row=0, column=7, padx=12)

        self._load_codes()

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="⟳  Refresh",      command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎  Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="⏹  End Record",    command=self._end_record).pack(side="left")

    def _build_tree(self):
        cols = ("id", "worker_code", "first_name", "last_name", "start_date", "end_date")
        self.tree = build_tree(self, cols, {"id": 90})

    def _load_codes(self):
        self._code_map.clear()
        try:
            for wc in api.get_active_worker_codes():
                label = f"{wc['code_name']} ({wc['code_id'][:8]}…)"
                self._code_map[label] = wc["code_id"]
            self.worker_code_cb["values"] = list(self._code_map.keys())
            if self._code_map:
                self.worker_code_cb.current(0)
        except Exception as e:
            messagebox.showerror("Error loading codes", str(e))

    def refresh(self):
        self._load_codes()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            all_codes = {wc["code_id"]: wc["code_name"] for wc in api.get_worker_codes()}
            for w in api.get_workers():
                self.tree.insert("", "end", iid=w["id"], values=(
                    w["id"][:8] + "…",
                    all_codes.get(w["worker_code"], "Unknown"),
                    w["first_name"],
                    w["last_name"],
                    w["start_date"] or "",
                    w["end_date"] or "",
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save(self):
        try:
            selected_label = self.worker_code_var.get()
            if not selected_label:
                messagebox.showerror("Validation", "Please select a Worker Code.")
                return
            first = self.first_name.get().strip()
            last  = self.last_name.get().strip()
            if not first or not last:
                messagebox.showerror("Validation", "First and Last Name are required.")
                return
            api.create_worker(self._code_map[selected_label], first, last)
            self.first_name.delete(0, tk.END)
            self.last_name.delete(0, tk.END)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select a row", "Please select a record first.")
            return None
        return sel[0]

    def _edit(self):
        iid = self._selected_id()
        if not iid:
            return
        row = next((w for w in api.get_workers() if w["id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(self, "Edit Worker", {
            "First Name": row["first_name"],
            "Last Name":  row["last_name"],
        })
        if dlg.result is None:
            return
        try:
            api.update_worker(iid, dlg.result["First Name"], dlg.result["Last Name"])
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _end_record(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm", "Set end date to today for this worker?"):
            return
        try:
            api.end_worker(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ─────────────────────────────────────────────
# WorkerTimes Tab
# ─────────────────────────────────────────────

class WorkerTimesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_form()
        self._build_controls()
        self._build_tree()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="  New Worker Time")
        form.pack(fill="x", padx=10, pady=(12, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=10)

        ttk.Label(fields, text="Time Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.time_name = ttk.Entry(fields, width=20)
        self.time_name.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="Start Time (HH:MM):").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.start_time = ttk.Entry(fields, width=10)
        self.start_time.grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(fields, text="End Time (HH:MM):").grid(row=0, column=4, sticky="e", padx=6, pady=4)
        self.end_time = ttk.Entry(fields, width=10)
        self.end_time.grid(row=0, column=5, sticky="w", padx=6, pady=4)

        ttk.Button(fields, text="Save", command=self._save).grid(row=0, column=6, padx=12)

    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Button(bar, text="⟳  Refresh",      command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎  Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="⏹  End Record",    command=self._end_record).pack(side="left")

    def _build_tree(self):
        cols = ("time_id", "time_name", "start_time", "end_time", "start_date", "end_date")
        self.tree = build_tree(self, cols, {"time_id": 90})

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            for wt in api.get_worker_times():
                self.tree.insert("", "end", iid=wt["time_id"], values=(
                    wt["time_id"][:8] + "…",
                    wt["time_name"],
                    (wt["start_time"] or "")[:5],
                    (wt["end_time"] or "")[:5],
                    wt["start_date"][:16] if wt["start_date"] else "",
                    wt["end_date"][:16] if wt["end_date"] else "",
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _parse_time(self, value: str):
        value = value.strip()
        if not value:
            return None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
        raise ValueError(f"Invalid time '{value}'. Use HH:MM.")

    def _save(self):
        try:
            name = self.time_name.get().strip()
            if not name:
                messagebox.showerror("Validation", "Time Name is required.")
                return
            start_t = self._parse_time(self.start_time.get())
            if start_t is None:
                messagebox.showerror("Validation", "Start Time is required.")
                return
            end_t = self._parse_time(self.end_time.get())
            api.create_worker_time(
                name,
                start_t.strftime("%H:%M:%S"),
                end_t.strftime("%H:%M:%S") if end_t else None,
            )
            self.time_name.delete(0, tk.END)
            self.start_time.delete(0, tk.END)
            self.end_time.delete(0, tk.END)
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select a row", "Please select a record first.")
            return None
        return sel[0]

    def _edit(self):
        iid = self._selected_id()
        if not iid:
            return
        row = next((wt for wt in api.get_worker_times() if wt["time_id"] == iid), None)
        if not row:
            return
        dlg = EditDialog(self, "Edit Worker Time", {
            "Time Name":           row["time_name"],
            "Start Time (HH:MM)":  (row["start_time"] or "")[:5],
            "End Time (HH:MM)":    (row["end_time"] or "")[:5],
        })
        if dlg.result is None:
            return
        try:
            start_t = self._parse_time(dlg.result["Start Time (HH:MM)"])
            end_t   = self._parse_time(dlg.result["End Time (HH:MM)"])
            api.update_worker_time(
                iid,
                dlg.result["Time Name"],
                start_t.strftime("%H:%M:%S") if start_t else "",
                end_t.strftime("%H:%M:%S") if end_t else None,
            )
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _end_record(self):
        iid = self._selected_id()
        if not iid:
            return
        if not messagebox.askyesno("Confirm", "Set end date to now for this record?"):
            return
        try:
            api.end_worker_time(iid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ─────────────────────────────────────────────
# Shared notebook builder
# ─────────────────────────────────────────────

def _build_notebook(window: tk.Misc):
    notebook = ttk.Notebook(window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    workers_tab      = WorkersTab(notebook)
    worker_codes_tab = WorkerCodesTab(notebook)
    worker_times_tab = WorkerTimesTab(notebook)

    notebook.add(workers_tab,      text="  Workers  ")
    notebook.add(worker_codes_tab, text="  Worker Codes  ")
    notebook.add(worker_times_tab, text="  Worker Times  ")

    return notebook


# ─────────────────────────────────────────────
# Main App  (standalone entry-point)
# ─────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Worker Management")
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)
        self.minsize(960, 560)

        _apply_style(self)
        _maximize(self)
        _build_header(self, "Worker Management",
                      "Santa Rita Farm  •  Manage worker codes, workers & shift times")
        _build_notebook(self)


# ─────────────────────────────────────────────
# Worker Management as a Toplevel child window
# (used by the Control Panel)
# ─────────────────────────────────────────────

class WorkerManagementWindow(tk.Toplevel):
    """Opens the Worker Management UI inside a Toplevel window so it can be
    launched from the Santa Rita Control Panel without spawning a second
    Tk root instance."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Worker Management")
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)
        self.minsize(960, 560)

        _apply_style(self)
        _maximize(self)
        _build_header(self, "Worker Management",
                      "Santa Rita Farm  •  Manage worker codes, workers & shift times")
        _build_notebook(self)

        # centre relative to parent — skipped since we maximise
        self.grab_set()
