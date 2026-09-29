# pages_leaderboard.py
import tkinter as tk
from tkinter import ttk
import data_store as ds

MATPLOTLIB_AVAILABLE = True
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
except Exception:
    MATPLOTLIB_AVAILABLE = False
    FigureCanvasTkAgg = None
    plt = None


def _top_rows(rows, ptype: str, top_n: int = 3):
    filtered = [r for r in rows if r.get("type") == ptype]
    return filtered[:top_n]


class LeaderboardPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app

        header = ttk.Frame(self, style="Content.TFrame")
        header.pack(fill="x", padx=30, pady=(26, 10))

        ttk.Label(header, text="الترتيب النهائي", style="Title.TLabel").pack(side="left")

        ttk.Button(
            header,
            text="تحديث الرسم",
            style="Primary.TButton",
            command=self.refresh_all,
        ).pack(side="right")

        self.status = ttk.Label(self, text="", style="Sub.TLabel")
        self.status.pack(anchor="w", padx=30, pady=(0, 10))

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=30, pady=(0, 26))

        self.tab_ind = ttk.Frame(self.nb)
        self.tab_team = ttk.Frame(self.nb)

        self.nb.add(self.tab_ind, text="الفردي")
        self.nb.add(self.tab_team, text="الفرق")

        self.ind_wrap = ttk.Frame(self.tab_ind, style="Content.TFrame")
        self.ind_wrap.pack(fill="both", expand=True)

        self.team_wrap = ttk.Frame(self.tab_team, style="Content.TFrame")
        self.team_wrap.pack(fill="both", expand=True)

        self.refresh_all()

    def _clear(self, box):
        for w in box.winfo_children():
            w.destroy()

    def _draw_top3(self, parent, title: str, rows: list[dict], type_label: str):
        self._clear(parent)

        top_box = ttk.Frame(parent, style="Content.TFrame")
        top_box.pack(fill="x", pady=(0, 12))

        top_box.grid_columnconfigure(0, weight=1)
        top_box.grid_columnconfigure(1, weight=1)
        top_box.grid_columnconfigure(2, weight=1)

        medals = ["🥇", "🥈", "🥉"]

        for i in range(3):
            card = ttk.Frame(top_box, style="Card.TFrame")
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))

            bar = tk.Frame(card, bg=self.app.COL_ACCENT, height=6)
            bar.pack(fill="x")

            body = ttk.Frame(card, style="Card.TFrame")
            body.pack(fill="both", expand=True, padx=14, pady=14)

            ttk.Label(body, text=f"{medals[i]} المركز {i+1}", style="CardTitle.TLabel").pack(anchor="w")

            if i < len(rows):
                r = rows[i]
                ttk.Label(body, text=r.get("name", "-"), style="CardText.TLabel").pack(anchor="w", pady=(8, 4))
                ttk.Label(body, text=f"Average: {r.get('avg', 0):.2f}", style="CardText.TLabel").pack(anchor="w")
                ttk.Label(body, text=f"Total: {r.get('total', 0):.2f}", style="CardText.TLabel").pack(anchor="w")
            else:
                ttk.Label(body, text="لا يوجد", style="CardText.TLabel").pack(anchor="w", pady=(8, 4))

        chart_box = ttk.Frame(parent, style="Card.TFrame")
        chart_box.pack(fill="both", expand=True)

        if not rows:
            ttk.Label(
                chart_box,
                text=f"لا يوجد نقاط مسجلة في قسم {type_label}",
                style="Sub.TLabel",
                justify="center"
            ).pack(pady=40)
            return

        if not MATPLOTLIB_AVAILABLE:
            ttk.Label(
                chart_box,
                text="matplotlib غير مثبتة\npython -m pip install matplotlib",
                style="Sub.TLabel",
                justify="center"
            ).pack(pady=40)
            return

        labels = [f"Rank {i+1}" for i in range(len(rows))]
        scores = [float(r.get("avg", 0.0)) for r in rows]

        fig = plt.Figure(figsize=(9.5, 4.6), dpi=100)
        ax = fig.add_subplot(111)

        colors = ["#FFD700", "#C0C0C0", "#cd7f32"][:len(scores)]

        ax.barh(labels[::-1], scores[::-1], color=colors[::-1])

        ax.set_title(title)
        ax.set_xlabel("Average Points (System A)")
        ax.set_ylabel("Rank")
        ax.grid(True, axis="x", linestyle="--", alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=chart_box)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def refresh_all(self):
        try:
            ds.load_state()
        except Exception:
            pass

        rows = ds.get_scores_table(method="avg")

        ind_rows = _top_rows(rows, "individual", 3)
        team_rows = _top_rows(rows, "team", 3)

        self._draw_top3(
            self.ind_wrap,
            title="Individuals - Top 3",
            rows=ind_rows,
            type_label="الفردي"
        )

        self._draw_top3(
            self.team_wrap,
            title="Teams - Top 3",
            rows=team_rows,
            type_label="الفرق"
        )

        self.status.config(
            text=f"Individuals with scores: {len([r for r in rows if r.get('type') == 'individual'])} | Teams with scores: {len([r for r in rows if r.get('type') == 'team'])}"
        )