import tkinter as tk
from tkinter import ttk
from datetime import datetime


# ─────────────────────────────────────────────
# Colour / style constants
# ─────────────────────────────────────────────

BG_MAIN      = "#f4f1ea"   # warm parchment
BG_HEADER    = "#1b3a1b"   # deep forest green
BG_CARD      = "#ffffff"
BG_CARD_HVR  = "#eaf3ea"
FG_HEADER    = "#ffffff"
FG_SUBTITLE  = "#a8c8a0"
FG_TITLE     = "#ffffff"
FG_CARD_TITLE= "#1b3a1b"
FG_CARD_DESC = "#555555"
ACCENT       = "#2e6b2e"
BORDER       = "#c8dfc8"


# ─────────────────────────────────────────────
# Module card widget
# ─────────────────────────────────────────────

class ModuleCard(tk.Frame):
    """A clickable card that launches one module of the control panel."""

    def __init__(self, parent, icon: str, title: str, description: str, command, **kwargs):
        super().__init__(
            parent,
            bg=BG_CARD,
            relief="flat",
            bd=0,
            highlightbackground=BORDER,
            highlightthickness=1,
            cursor="hand2",
            **kwargs,
        )

        # ── icon row ──
        tk.Label(self, text=icon, font=("Helvetica", 28),
                 bg=BG_CARD, fg=ACCENT).pack(pady=(18, 4))

        # ── title ──
        tk.Label(self, text=title, font=("Helvetica", 13, "bold"),
                 bg=BG_CARD, fg=FG_CARD_TITLE).pack()

        # ── description ──
        tk.Label(self, text=description, font=("Helvetica", 9),
                 bg=BG_CARD, fg=FG_CARD_DESC, wraplength=160,
                 justify="center").pack(pady=(4, 18))

        # bind click + hover to every child widget as well
        for widget in (self, *self.winfo_children()):
            widget.bind("<Button-1>", lambda _e: command())
            widget.bind("<Enter>",    lambda _e: self._hover(True))
            widget.bind("<Leave>",    lambda _e: self._hover(False))

    def _hover(self, on: bool):
        colour = BG_CARD_HVR if on else BG_CARD
        self.configure(bg=colour)
        for child in self.winfo_children():
            try:
                child.configure(bg=colour)
            except tk.TclError:
                pass


# ─────────────────────────────────────────────
# Live clock label
# ─────────────────────────────────────────────

class ClockLabel(tk.Label):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._tick()

    def _tick(self):
        now = datetime.now().strftime("%A, %d %B %Y    %H:%M:%S")
        self.configure(text=now)
        self.after(1000, self._tick)


# ─────────────────────────────────────────────
# Main Control Panel window
# ─────────────────────────────────────────────

class ControlPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Santa Rita Control Panel")
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)
        self.minsize(720, 500)

        self._build_header()
        self._build_welcome()
        self._build_modules()
        self._build_footer()

        # maximise on open (cross-platform)
        ws = self.tk.call("tk", "windowingsystem")
        if ws == "win32":
            self.state("zoomed")
        elif ws == "x11":
            self.attributes("-zoomed", True)
        else:  # aqua (macOS)
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

    # ── Header ──────────────────────────────────

    def _build_header(self):
        header = tk.Frame(self, bg=BG_HEADER)
        header.pack(fill="x")

        # left: logo text
        left = tk.Frame(header, bg=BG_HEADER)
        left.pack(side="left", padx=24, pady=16)

        tk.Label(left, text="🌿  Santa Rita",
                 font=("Helvetica", 22, "bold"),
                 bg=BG_HEADER, fg=FG_TITLE).pack(anchor="w")

        tk.Label(left, text="Control Panel",
                 font=("Helvetica", 12),
                 bg=BG_HEADER, fg=FG_SUBTITLE).pack(anchor="w")

        # right: live clock
        ClockLabel(header,
                   font=("Courier", 11),
                   bg=BG_HEADER, fg=FG_SUBTITLE).pack(
            side="right", padx=24, pady=16)

    # ── Welcome banner ───────────────────────────

    def _build_welcome(self):
        banner = tk.Frame(self, bg=ACCENT)
        banner.pack(fill="x")

        tk.Label(
            banner,
            text="Welcome back.  Select a module below to get started.",
            font=("Helvetica", 10),
            bg=ACCENT, fg="#dff0df",
            pady=6,
        ).pack()

    # ── Module grid ──────────────────────────────

    def _build_modules(self):
        outer = tk.Frame(self, bg=BG_MAIN)
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        # Section heading
        tk.Label(outer, text="Modules",
                 font=("Helvetica", 11, "bold"),
                 bg=BG_MAIN, fg="#444444").pack(anchor="w", pady=(0, 12))

        # Card grid frame
        grid = tk.Frame(outer, bg=BG_MAIN)
        grid.pack(fill="both", expand=True)

        # ── define all modules here ──────────────
        # To add a new module, append a dict to this list.
        modules = [
            {
                "icon":        "👷",
                "title":       "Worker Management",
                "description": "Manage workers, worker codes and shift times.",
                "command":     self._open_worker_management,
            },
            # ── future modules go here ────────────
            # {
            #     "icon":        "🏡",
            #     "title":       "Site Management",
            #     "description": "Manage farm sites and locations.",
            #     "command":     self._open_site_management,
            # },
            # {
            #     "icon":        "📦",
            #     "title":       "Inventory",
            #     "description": "Track stock and farm supplies.",
            #     "command":     self._open_inventory,
            # },
        ]

        COLS = 4   # max cards per row
        for i, mod in enumerate(modules):
            card = ModuleCard(
                grid,
                icon=mod["icon"],
                title=mod["title"],
                description=mod["description"],
                command=mod["command"],
                width=180,
                height=160,
            )
            card.grid(
                row=i // COLS, column=i % COLS,
                padx=10, pady=10, sticky="nsew",
            )
            card.grid_propagate(False)

        # make columns expand evenly
        for c in range(COLS):
            grid.columnconfigure(c, weight=1)

    # ── Footer ───────────────────────────────────

    def _build_footer(self):
        footer = tk.Frame(self, bg=BG_HEADER)
        footer.pack(fill="x", side="bottom")
        tk.Label(
            footer,
            text="Santa Rita Farm  •  Internal Operations Platform",
            font=("Helvetica", 8),
            bg=BG_HEADER, fg=FG_SUBTITLE,
            pady=6,
        ).pack()

    # ── Module launchers ─────────────────────────

    def _open_worker_management(self):
        # Import here to avoid circular imports at module load time
        from app.gui import WorkerManagementWindow
        WorkerManagementWindow(self)

    def _open_org_management(self):
        from app.org_gui import OrgManagementWindow
        OrgManagementWindow(self)

