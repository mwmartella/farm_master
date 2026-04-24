import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import app.api_client as api


# ─────────────────────────────────────────────
# Shared Edit Dialog
# ─────────────────────────────────────────────

class EditDialog(tk.Toplevel):
    """Generic dialog for editing a set of named fields."""

    def __init__(self, parent, title: str, fields: dict):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        self._entries = {}
        for row, (label, value) in enumerate(fields.items()):
            ttk.Label(self, text=label + ":").grid(row=row, column=0, sticky="e", padx=10, pady=6)
            e = ttk.Entry(self, width=30)
            e.insert(0, str(value) if value is not None else "")
            e.grid(row=row, column=1, sticky="w", padx=10, pady=6)
            self._entries[label] = e

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self._ok).pack(side="left", padx=6)
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
    frame.pack(fill="both", expand=True, padx=6, pady=6)

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
        form = ttk.LabelFrame(self, text="New Worker Code")
        form.pack(fill="x", padx=10, pady=(10, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=8)

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
        bar.pack(fill="x", padx=10, pady=(6, 0))
        ttk.Button(bar, text="⟳ Refresh", command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎ Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="⏹ End Record", command=self._end_record).pack(side="left")

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
            "Code Name": row["code_name"],
            "Description": row["code_description"],
            "Pay Rate": row["pay_rate"],
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
        form = ttk.LabelFrame(self, text="New Worker")
        form.pack(fill="x", padx=10, pady=(10, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=8)

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
        bar.pack(fill="x", padx=10, pady=(6, 0))
        ttk.Button(bar, text="⟳ Refresh", command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎ Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="⏹ End Record", command=self._end_record).pack(side="left")

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
            # Build a code_id -> code_name lookup from all codes (including ended)
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
            last = self.last_name.get().strip()
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
            "Last Name": row["last_name"],
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
        form = ttk.LabelFrame(self, text="New Worker Time")
        form.pack(fill="x", padx=10, pady=(10, 0))

        fields = ttk.Frame(form)
        fields.pack(side="left", padx=10, pady=8)

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
        bar.pack(fill="x", padx=10, pady=(6, 0))
        ttk.Button(bar, text="⟳ Refresh", command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✎ Edit Selected", command=self._edit).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="⏹ End Record", command=self._end_record).pack(side="left")

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
            "Time Name": row["time_name"],
            "Start Time (HH:MM)": (row["start_time"] or "")[:5],
            "End Time (HH:MM)": (row["end_time"] or "")[:5],
        })
        if dlg.result is None:
            return
        try:
            start_t = self._parse_time(dlg.result["Start Time (HH:MM)"])
            end_t = self._parse_time(dlg.result["End Time (HH:MM)"])
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
# Main App
# ─────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Worker Management")
        self.resizable(True, True)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.worker_codes_tab = WorkerCodesTab(notebook)
        self.workers_tab = WorkersTab(notebook)
        self.worker_times_tab = WorkerTimesTab(notebook)

        notebook.add(self.worker_codes_tab, text="  Worker Codes  ")
        notebook.add(self.workers_tab, text="  Workers  ")
        notebook.add(self.worker_times_tab, text="  Worker Times  ")

