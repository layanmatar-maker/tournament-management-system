# pages_points.py
import tkinter as tk
from tkinter import ttk
import data_store as ds


class PointsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app

        header = ttk.Frame(self, style="Content.TFrame")
        header.pack(fill="x", padx=30, pady=(26, 10))

        ttk.Label(header, text="عرض النقاط", style="Title.TLabel").pack(side="left")

        ttk.Button(
            header, text="تحديث", style="Primary.TButton",
            command=self.refresh_table
        ).pack(side="right")

        self.status = ttk.Label(self, text="", style="Sub.TLabel")
        self.status.pack(anchor="w", padx=30, pady=(0, 10))

        box = ttk.Frame(self, style="Content.TFrame")
        box.pack(fill="both", expand=True, padx=30, pady=(0, 26))

        # ✅ نظام A: الترتيب حسب المتوسط (avg) عشان ما يكون ظلم
        cols = ("rank", "ptype", "name", "events", "avg", "total")
        self.tree = ttk.Treeview(box, columns=cols, show="headings")

        self.tree.heading("rank", text="الترتيب")
        self.tree.heading("ptype", text="النوع")
        self.tree.heading("name", text="الاسم")
        self.tree.heading("events", text="عدد الفعاليات")
        self.tree.heading("avg", text="المتوسط")
        self.tree.heading("total", text="المجموع")

        self.tree.column("rank", width=90, anchor="center")
        self.tree.column("ptype", width=120, anchor="center")
        self.tree.column("name", width=320, anchor="w")
        self.tree.column("events", width=120, anchor="center")
        self.tree.column("avg", width=140, anchor="center")
        self.tree.column("total", width=140, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        sb.pack(side="left", fill="y", padx=(6, 0))
        self.tree.configure(yscrollcommand=sb.set)

        self.refresh_table()

    def refresh_table(self):
        ds.load_state()
        rows = ds.get_scores_table(method="avg")  # ✅ ترتيب حسب المتوسط
        self.tree.delete(*self.tree.get_children())

        for i, r in enumerate(rows, start=1):
            ptype_ar = "فردي" if r["type"] == "individual" else "فرقة"
            self.tree.insert(
                "", "end",
                values=(i, ptype_ar, r["name"], r["events_count"], f"{r['avg']:.2f}", f"{r['total']:.2f}")
            )

        self.status.config(text=f"عدد المشاركين اللي عليهم نقاط: {len(rows)} | الترتيب حسب المتوسط (نظام A)")