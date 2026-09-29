# pages_results.py
import tkinter as tk
from tkinter import ttk, messagebox
import data_store as ds
from config import EVENTS
import data_store as ds

def _event_name(eid: int) -> str:
    for e in EVENTS:
        if e["id"] == eid:
            return e["name"]
    return str(eid)


def _event_mode(eid: int) -> str:
    for e in EVENTS:
        if e["id"] == eid:
            return e["mode"]
    return ""


class ResultsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app

        header = ttk.Frame(self, style="Content.TFrame")
        header.pack(fill="x", padx=30, pady=(26, 10))
        ttk.Label(header, text="ادخال النتائج", style="Title.TLabel").pack(side="left")

        ttk.Button(
            header, text="حذف كل النقاط", style="Primary.TButton",
            command=self.delete_all_scores
        ).pack(side="right")

        ttk.Button(
            header, text="تحديث", style="Primary.TButton",
            command=self.refresh_lists
        ).pack(side="right", padx=(0, 10))

        ttk.Button(
          header,
                    text="Export Excel",
            style="Primary.TButton",
            command=lambda: ds.export_to_excel()
        ).pack(side="right", padx=10)


        self.status = ttk.Label(self, text="", style="Sub.TLabel")
        self.status.pack(anchor="w", padx=30, pady=(0, 10))

        wrap = ttk.Frame(self, style="Content.TFrame")
        wrap.pack(fill="both", expand=True, padx=30, pady=(0, 26))

        # النوع
        mode_row = ttk.Frame(wrap, style="Content.TFrame")
        mode_row.pack(fill="x", pady=(0, 10))

        ttk.Label(mode_row, text="النوع:", style="Sub.TLabel").pack(side="left", padx=(0, 10))

        self.mode_var = tk.StringVar(value="individual")
        ttk.Radiobutton(
            mode_row, text="فردي", value="individual",
            variable=self.mode_var, command=self._on_mode_change
        ).pack(side="left", padx=6)

        ttk.Radiobutton(
            mode_row, text="فرقة", value="team",
            variable=self.mode_var, command=self._on_mode_change
        ).pack(side="left", padx=6)

        # الاسم والفعالية والنقاط
        sel_row = ttk.Frame(wrap, style="Content.TFrame")
        sel_row.pack(fill="x", pady=(0, 10))

        ttk.Label(sel_row, text="اسم المشارك:", style="Sub.TLabel").pack(side="left", padx=(0, 10))
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(sel_row, textvariable=self.name_var, state="readonly", width=35)
        self.name_combo.pack(side="left")
        self.name_combo.bind("<<ComboboxSelected>>", self._on_name_change)

        ttk.Label(sel_row, text="الفعالية:", style="Sub.TLabel").pack(side="left", padx=(20, 10))
        self.event_var = tk.StringVar()
        self.event_combo = ttk.Combobox(sel_row, textvariable=self.event_var, state="readonly", width=28)
        self.event_combo.pack(side="left")

        ttk.Label(sel_row, text="النقاط:", style="Sub.TLabel").pack(side="left", padx=(20, 10))
        self.score_var = tk.StringVar()
        self.score_entry = ttk.Entry(sel_row, textvariable=self.score_var, width=10)
        self.score_entry.pack(side="left")

        ttk.Button(
            sel_row, text="ادخال", style="Primary.TButton",
            command=self.save_score
        ).pack(side="left", padx=(20, 0))

        self.score_entry.bind("<Return>", lambda _e: self.save_score())

        # جدول
        table_box = ttk.Frame(wrap, style="Content.TFrame")
        table_box.pack(fill="both", expand=True, pady=(14, 0))

        cols = ("ptype", "name", "event", "score")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings")

        self.tree.heading("ptype", text="النوع")
        self.tree.heading("name", text="الاسم")
        self.tree.heading("event", text="الفعالية")
        self.tree.heading("score", text="النقاط")

        self.tree.column("ptype", width=100, anchor="center")
        self.tree.column("name", width=240, anchor="w")
        self.tree.column("event", width=260, anchor="w")
        self.tree.column("score", width=100, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        sb.pack(side="left", fill="y", padx=(6, 0))
        self.tree.configure(yscrollcommand=sb.set)

        self.refresh_lists()
        self.refresh_table()

    def _participant_event_ids(self, ptype: str, name: str):
        ds.load_state()
        for p in ds.list_participants():
            if p.get("type") == ptype and p.get("name") == name:
                return [int(x) for x in (p.get("event_ids") or [])]
        return []

    def _set_events_for_selected_participant(self):
        mode = self.mode_var.get()
        name = (self.name_var.get() or "").strip()
        ids = self._participant_event_ids(mode, name)
        ids = [eid for eid in ids if _event_mode(eid) == mode]

        items = [f"{eid} - {_event_name(eid)}" for eid in ids]
        self.event_combo["values"] = items
        self.event_var.set(items[0] if items else "")

    def _on_name_change(self, _evt=None):
        self._set_events_for_selected_participant()

    def _on_mode_change(self):
        self.refresh_lists()

    def refresh_lists(self):
        ds.load_state()
        mode = self.mode_var.get()

        if mode == "individual":
            names = sorted(list((ds.individuals or {}).keys()))
        else:
            names = sorted(list((ds.teams or {}).keys()))

        self.name_combo["values"] = names
        self.name_var.set(names[0] if names else "")
        self._set_events_for_selected_participant()

        chosen = (self.name_var.get() or "").strip()
        cnt = len(self._participant_event_ids(mode, chosen)) if chosen else 0
        self.status.config(text=f"مشاركين: {len(names)} | فعاليات للمشارك المختار: {cnt}")

    def save_score(self):
        mode = self.mode_var.get()
        name = (self.name_var.get() or "").strip()
        ev_text = (self.event_var.get() or "").strip()
        sc_text = (self.score_var.get() or "").strip()

        if not name:
            messagebox.showerror("خطأ", "اختاري اسم مشارك")
            return
        if not ev_text or "-" not in ev_text:
            messagebox.showerror("خطأ", "اختاري فعالية")
            return
        if not sc_text:
            messagebox.showerror("خطأ", "اكتبي النقاط")
            return

        try:
            eid = int(ev_text.split("-")[0].strip())
        except Exception:
            messagebox.showerror("خطأ", "فعالية غير صحيحة")
            return

        allowed = self._participant_event_ids(mode, name)
        if eid not in allowed:
            messagebox.showerror("ممنوع", "هذا المشارك مش مسجل بهاي الفعالية")
            return

        try:
            score = float(sc_text)
        except Exception:
            messagebox.showerror("خطأ", "النقاط لازم تكون رقم")
            return

        ds.add_score(mode, name, eid, score)
        self.score_var.set("")
        messagebox.showinfo("تم", f"تم حفظ نقاط {name} في {_event_name(eid)} ✅")
        self.refresh_table()

    def refresh_table(self):
        ds.load_state()
        self.tree.delete(*self.tree.get_children())

        for key, details in (ds.event_scores or {}).items():
            if ":" in key:
                ptype, name = key.split(":", 1)
            else:
                ptype, name = "individual", key

            ptype_ar = "فردي" if ptype == "individual" else "فرقة"

            for eid_str, score in (details or {}).items():
                try:
                    eid = int(eid_str)
                except Exception:
                    continue
                self.tree.insert("", "end", values=(ptype_ar, name, _event_name(eid), score))

    def delete_all_scores(self):
        ok = messagebox.askyesno("تأكيد", "هل انت متأكد انك ستحذف جميع النقاط؟")
        if not ok:
            return
        ds.delete_all_scores()
        self.refresh_table()
        messagebox.showinfo("تم", "تم حذف جميع النقاط ✅")