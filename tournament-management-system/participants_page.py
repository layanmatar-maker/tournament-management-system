# participants_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import data_store as ds
from config import EVENTS


def _event_name(eid: int) -> str:
    for e in EVENTS:
        if e["id"] == eid:
            return e["name"]
    return str(eid)


def _event_mode(eid: int) -> str:
    for e in EVENTS:
        if e["id"] == eid:
            return e["mode"]  # "individual" / "team"
    return ""


class ParticipantsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app

        header = ttk.Frame(self, style="Content.TFrame")
        header.pack(fill="x", padx=30, pady=(26, 10))

        ttk.Label(header, text="ادارة المشاركين", style="Title.TLabel").pack(side="left")

        # زر حذف الكل
        ttk.Button(
            header,
            text="حذف جميع المشاركين",
            style="Primary.TButton",
            command=self.delete_all_participants,
        ).pack(side="right")

        # زر تحديث
        ttk.Button(
            header,
            text="تحديث",
            style="Primary.TButton",
            command=self.refresh_all,
        ).pack(side="right", padx=(0, 10))

        self.status = ttk.Label(self, text="", style="Sub.TLabel")
        self.status.pack(anchor="w", padx=30, pady=(0, 10))

        # Tabs
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=30, pady=(0, 26))

        self.tab_all = ttk.Frame(self.nb)
        self.tab_ind = ttk.Frame(self.nb)
        self.tab_team = ttk.Frame(self.nb)

        self.nb.add(self.tab_all, text="الكل")
        self.nb.add(self.tab_ind, text="فعاليات فردية")
        self.nb.add(self.tab_team, text="فعاليات الفرق")

        self.tree_all = self._build_table(self.tab_all)
        self.tree_ind = self._build_table(self.tab_ind)
        self.tree_team = self._build_table(self.tab_team)

        self.refresh_all()

    def _build_table(self, parent):
        wrap = ttk.Frame(parent, style="Content.TFrame")
        wrap.pack(fill="both", expand=True)

        cols = ("ptype", "name", "count", "events")
        tree = ttk.Treeview(wrap, columns=cols, show="headings")

        tree.heading("ptype", text="النوع")
        tree.heading("name", text="الاسم")
        tree.heading("count", text="عدد الفعاليات")
        tree.heading("events", text="اسماء الفعاليات")

        tree.column("ptype", width=120, anchor="center")
        tree.column("name", width=240, anchor="w")
        tree.column("count", width=140, anchor="center")
        tree.column("events", width=520, anchor="w")

        tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        sb.pack(side="left", fill="y", padx=(6, 0))
        tree.configure(yscrollcommand=sb.set)

        return tree

    def _collect_rows(self):
        """يجمع كل المشاركين من كل المصادر"""
        try:
            ds.load_state()
        except Exception:
            pass

        rows = []

        # participant_events
        pe = getattr(ds, "participant_events", {}) or {}
        for _key, item in pe.items():
            ptype = item.get("type", "")
            name = item.get("name", "")
            evs = item.get("event_ids", []) or []
            if not name:
                continue
            rows.append({"ptype": ptype, "name": name, "event_ids": [int(x) for x in evs]})

        # fallback individuals
        inds = getattr(ds, "individuals", {}) or {}
        for name, item in inds.items():
            if any(r["ptype"] == "individual" and r["name"] == name for r in rows):
                continue
            evs = (item or {}).get("event_ids", []) or []
            rows.append({"ptype": "individual", "name": name, "event_ids": [int(x) for x in evs]})

        # fallback teams
        teams = getattr(ds, "teams", {}) or {}
        for name, item in teams.items():
            if any(r["ptype"] == "team" and r["name"] == name for r in rows):
                continue
            evs = (item or {}).get("event_ids", []) or []
            rows.append({"ptype": "team", "name": name, "event_ids": [int(x) for x in evs]})

        rows.sort(key=lambda r: (r["ptype"], r["name"]))
        return rows

    def _fill_tree(self, tree, rows):
        tree.delete(*tree.get_children())
        for r in rows:
            ptype_ar = "فردي" if r["ptype"] == "individual" else "فرقة"
            ev_names = ", ".join(_event_name(eid) for eid in r["event_ids"])
            tree.insert("", "end", values=(ptype_ar, r["name"], len(r["event_ids"]), ev_names))

    def refresh_all(self):
        rows = self._collect_rows()

        # الكل
        self._fill_tree(self.tree_all, rows)

        # فردي
        ind_rows = []
        for r in rows:
            if r["ptype"] != "individual":
                continue
            only_ind_events = [eid for eid in r["event_ids"] if _event_mode(eid) == "individual"]
            ind_rows.append({"ptype": r["ptype"], "name": r["name"], "event_ids": only_ind_events})
        self._fill_tree(self.tree_ind, ind_rows)

        # فرق
        team_rows = []
        for r in rows:
            if r["ptype"] != "team":
                continue
            only_team_events = [eid for eid in r["event_ids"] if _event_mode(eid) == "team"]
            team_rows.append({"ptype": r["ptype"], "name": r["name"], "event_ids": only_team_events})
        self._fill_tree(self.tree_team, team_rows)

        self.status.config(text=f"الكل: {len(rows)} | فردي: {len(ind_rows)} | فرق: {len(team_rows)}")

    def delete_all_participants(self):
        ok = messagebox.askyesno(
            "تأكيد الحذف",
            "هل انت متأكد انك ستحذف اسامي المشاركين؟"
        )
        if not ok:
            return

        # تفريغ بيانات المشاركين
        ds.teams.clear()
        ds.individuals.clear()
        ds.participant_events.clear()
        ds.event_registrations.clear()
        ds.event_scores.clear()

        ds.save_state()
        self.refresh_all()

        messagebox.showinfo("تم", "تم حذف جميع المشاركين ✅")