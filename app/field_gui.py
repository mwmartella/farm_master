"""
Field Management GUI
Manages the Fields database table.
Launched from the Santa Rita Control Panel.
"""

import tkinter as tk
from tkinter import ttk

from app.org_gui import (
    FieldsTab,
    _apply_style,
    _maximize,
    _build_header,
)
from app.planting_gui import BlocksTab


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

        fields_tab = FieldsTab(notebook)
        notebook.add(fields_tab, text="  Fields  ")
        notebook.add(BlocksTab(notebook), text="  Blocks  ")

        self.grab_set()

