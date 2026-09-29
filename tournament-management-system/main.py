# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from config import ADMIN_PASSWORD, MAX_TEAMS, MAX_INDIVIDUALS, EVENTS, THEME
import data_store as ds

from pages_registration import RegistrationPage
from pages_instructions import InstructionsPage

from participants_page import ParticipantsPage
from pages_results import ResultsPage
from pages_points import PointsPage

from pages_leaderboard import LeaderboardPage
from pages_admin_chat import AdminChatPage


class PlaceholderPage(ttk.Frame):
    def __init__(self, parent, title: str, subtitle: str, app):
        super().__init__(parent, style="Content.TFrame")
        wrap = ttk.Frame(self, style="Content.TFrame")
        wrap.pack(fill="both", expand=True, padx=30, pady=30)
        ttk.Label(wrap, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(wrap, text=subtitle, style="Sub.TLabel").pack(anchor="w", pady=(6, 18))


class HomePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app

        try:
            ds.load_state()
        except Exception:
            pass

        header = ttk.Frame(self, style="Content.TFrame")
        header.pack(fill="x", padx=30, pady=(26, 12))
        ttk.Label(header, text="Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Quick stats", style="Sub.TLabel").pack(anchor="w", pady=(6, 0))

        cards = ttk.Frame(self, style="Content.TFrame")
        cards.pack(fill="x", padx=30, pady=(16, 8))
        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)
        cards.grid_columnconfigure(2, weight=1)

        self._stat_card(cards, "Teams", f"{len(ds.teams)}/{MAX_TEAMS}", app.COL_ACCENT).grid(
            row=0, column=0, sticky="nsew", padx=(0, 12)
        )
        self._stat_card(cards, "Individuals", f"{len(ds.individuals)}/{MAX_INDIVIDUALS}", app.COL_OK).grid(
            row=0, column=1, sticky="nsew", padx=12
        )
        self._stat_card(cards, "Events", f"{len(EVENTS)}", app.COL_WARN).grid(
            row=0, column=2, sticky="nsew", padx=(12, 0)
        )

        panel = ttk.Frame(self, style="Card.TFrame")
        panel.pack(fill="both", expand=True, padx=30, pady=(18, 26))

        bar = tk.Frame(panel, bg=app.COL_ACCENT, height=6)
        bar.pack(fill="x")

        body = ttk.Frame(panel, style="Card.TFrame")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        if app.is_admin:
            role = getattr(app, "admin_role", "Admin")
            ttk.Label(body, text=f"Admin Panel ({role})", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
            ttk.Label(body, text="Pick a page from the left menu.", style="CardText.TLabel").pack(anchor="w")
        else:
            ttk.Label(body, text="Hello", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
            ttk.Label(body, text="Go to Registration or Instructions from the left menu.", style="CardText.TLabel").pack(anchor="w")

    def _stat_card(self, parent, title, value, accent):
        card = ttk.Frame(parent, style="Card.TFrame")
        bar = tk.Frame(card, bg=accent, height=6)
        bar.pack(fill="x")
        body = ttk.Frame(card, style="Card.TFrame")
        body.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(body, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(body, text=value, style="CardText.TLabel").pack(anchor="w", pady=(6, 0))
        return card


class TournamentApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("College Tournament System")
        self.geometry("1100x650")
        self.minsize(1000, 600)

        self.is_admin = False
        self.admin_role = None  # ✅ "Admin 1" / "Admin 2"

        # Theme
        self.COL_BG = THEME["BG"]
        self.COL_PANEL = THEME["PANEL"]
        self.COL_CARD = THEME["CARD"]
        self.COL_TEXT = THEME["TEXT"]
        self.COL_MUTED = THEME["MUTED"]
        self.COL_ACCENT = THEME["ACCENT"]
        self.COL_OK = THEME["OK"]
        self.COL_WARN = THEME["WARN"]

        self.configure(bg=self.COL_BG)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Base styles
        self.style.configure("TFrame", background=self.COL_BG)
        self.style.configure("Sidebar.TFrame", background=self.COL_PANEL)
        self.style.configure("Content.TFrame", background=self.COL_BG)

        self.style.configure("Title.TLabel", background=self.COL_BG, foreground=self.COL_TEXT,
                             font=("Segoe UI", 20, "bold"))
        self.style.configure("Sub.TLabel", background=self.COL_BG, foreground=self.COL_MUTED,
                             font=("Segoe UI", 11))

        self.style.configure("Sidebar.TLabel", background=self.COL_PANEL, foreground=self.COL_TEXT,
                             font=("Segoe UI", 12, "bold"))

        self.style.configure("Nav.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        self.style.map("Nav.TButton",
                       background=[("active", self.COL_ACCENT)],
                       foreground=[("active", "#001018")])

        self.style.configure("Card.TFrame", background=self.COL_CARD, relief="flat")
        self.style.configure("CardTitle.TLabel", background=self.COL_CARD, foreground=self.COL_TEXT,
                             font=("Segoe UI", 13, "bold"))
        self.style.configure("CardText.TLabel", background=self.COL_CARD, foreground=self.COL_MUTED,
                             font=("Segoe UI", 10))
        self.style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=10)

        # Treeview styling
        self.style.configure(
            "Treeview",
            background=self.COL_CARD,
            fieldbackground=self.COL_CARD,
            foreground=self.COL_TEXT,
            rowheight=28,
            borderwidth=0,
        )
        self.style.map(
            "Treeview",
            background=[("selected", self.COL_ACCENT)],
            foreground=[("selected", "#001018")],
        )
        self.style.configure(
            "Treeview.Heading",
            background=self.COL_PANEL,
            foreground=self.COL_TEXT,
            font=("Segoe UI", 11, "bold"),
        )

        self._build_layout()
        self.show_page("home")

    def _build_layout(self):
        root = ttk.Frame(self, style="TFrame")
        root.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(root, style="Sidebar.TFrame", width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ttk.Frame(root, style="Content.TFrame")
        self.content.pack(side="left", fill="both", expand=True)

        self.build_sidebar()

    def build_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()

        top = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        top.pack(fill="x", padx=18, pady=(18, 10))

        logo = tk.Canvas(top, width=44, height=44, bg=self.COL_PANEL, highlightthickness=0)
        logo.grid(row=0, column=0, rowspan=2, sticky="w")
        logo.create_oval(6, 6, 38, 38, fill=self.COL_ACCENT, outline="")
        logo.create_text(22, 22, text="C", fill="#001018", font=("Segoe UI", 14, "bold"))

        ttk.Label(top, text="College Tournament", style="Sidebar.TLabel").grid(row=0, column=1, sticky="w", padx=10)
        tk.Label(top, text="Tournament System", bg=self.COL_PANEL, fg=self.COL_MUTED,
                 font=("Segoe UI", 10)).grid(row=1, column=1, sticky="w", padx=10)

        nav = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        nav.pack(fill="x", padx=14, pady=(10, 14))

        # common
        ttk.Button(nav, text="Home", style="Nav.TButton",
                   command=lambda: self.show_page("home")).pack(fill="x", pady=6)

        if self.is_admin:
            ttk.Button(nav, text="Participants", style="Nav.TButton",
                       command=lambda: self.show_page("participants")).pack(fill="x", pady=6)
            ttk.Button(nav, text="Enter Results", style="Nav.TButton",
                       command=lambda: self.show_page("results")).pack(fill="x", pady=6)
            ttk.Button(nav, text="Points", style="Nav.TButton",
                       command=lambda: self.show_page("points")).pack(fill="x", pady=6)
            ttk.Button(nav, text="Leaderboard", style="Nav.TButton",
                       command=lambda: self.show_page("leaderboard")).pack(fill="x", pady=6)

            # ✅ NEW: admin chat
            ttk.Button(nav, text="Admin Chat", style="Nav.TButton",
                       command=lambda: self.show_page("admin_chat")).pack(fill="x", pady=6)

            ttk.Button(nav, text="Logout", style="Nav.TButton",
                       command=self.logout_admin).pack(fill="x", pady=(12, 6))
        else:
            ttk.Button(nav, text="Registration", style="Nav.TButton",
                       command=lambda: self.show_page("registration")).pack(fill="x", pady=6)
            ttk.Button(nav, text="Instructions", style="Nav.TButton",
                       command=lambda: self.show_page("instructions")).pack(fill="x", pady=6)
            ttk.Button(nav, text="Points", style="Nav.TButton",
                       command=lambda: self.show_page("points")).pack(fill="x", pady=6)
            ttk.Button(nav, text="Leaderboard", style="Nav.TButton",
                       command=lambda: self.show_page("leaderboard")).pack(fill="x", pady=6)
            ttk.Button(nav, text="Admin Mode", style="Nav.TButton",
                       command=self.login_admin).pack(fill="x", pady=(12, 6))

        footer = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        footer.pack(side="bottom", fill="x", padx=14, pady=14)

        role = "Student"
        if self.is_admin:
            role = getattr(self, "admin_role", "Admin") or "Admin"
        tk.Label(footer, text=f"Status: {role}", bg=self.COL_PANEL, fg=self.COL_MUTED,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

    def login_admin(self):
        pw = simpledialog.askstring("Admin Access", "Enter admin password", show="*")
        if pw is None:
            return

        if pw != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Wrong password")
            return

        # ✅ choose admin identity (1 or 2) using same password
        role = simpledialog.askstring("Admin Identity", "Type Admin 1 or Admin 2")
        if role is None:
            return
        role = role.strip().lower()

        if role in ("admin 1", "1", "a1", "first"):
            self.admin_role = "Admin 1"
        elif role in ("admin 2", "2", "a2", "second"):
            self.admin_role = "Admin 2"
        else:
            # default if they typed something weird
            self.admin_role = "Admin 1"

        self.is_admin = True
        messagebox.showinfo("Done", f"Logged in as {self.admin_role}")
        self.build_sidebar()
        self.show_page("home")

    def logout_admin(self):
        self.is_admin = False
        self.admin_role = None
        messagebox.showinfo("Done", "Logged out")
        self.build_sidebar()
        self.show_page("home")

    def _require_admin(self) -> bool:
        if self.is_admin:
            return True
        messagebox.showwarning("Access required", "This page is admin-only")
        self.login_admin()
        return self.is_admin

    def show_page(self, page_name: str):
        for w in self.content.winfo_children():
            w.destroy()

        # always refresh data when switching pages (prevents stale UI)
        try:
            ds.load_state()
        except Exception:
            pass

        if page_name == "home":
            HomePage(self.content, app=self).pack(fill="both", expand=True)

        elif page_name == "registration":
            RegistrationPage(self.content, app=self).pack(fill="both", expand=True)

        elif page_name == "instructions":
            InstructionsPage(self.content, app=self).pack(fill="both", expand=True)

        elif page_name == "participants":
            if not self._require_admin():
                return
            ParticipantsPage(self.content, app=self).pack(fill="both", expand=True)

        elif page_name == "results":
            if not self._require_admin():
                return
            ResultsPage(self.content, app=self).pack(fill="both", expand=True)

        elif page_name == "points":
            PointsPage(self.content, app=self).pack(fill="both", expand=True)

        elif page_name == "leaderboard":
            LeaderboardPage(self.content, app=self).pack(fill="both", expand=True)

        elif page_name == "admin_chat":
            if not self._require_admin():
                return
            AdminChatPage(self.content, app=self).pack(fill="both", expand=True)

        else:
            PlaceholderPage(self.content, "Page", "Unknown page", self).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = TournamentApp()
    app.mainloop()