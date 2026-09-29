# pages_registration.py
import tkinter as tk
from tkinter import ttk, messagebox

from config import EVENTS, MAX_EVENTS_PER_PARTICIPANT, MAX_TEAMS, MAX_INDIVIDUALS
import data_store as ds


def get_event_by_id(eid: int):
    for e in EVENTS:
        if e["id"] == eid:
            return e
    return None


class RegistrationPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app

        wrap = ttk.Frame(self, style="Content.TFrame")
        wrap.pack(fill="both", expand=True, padx=30, pady=30)

        ttk.Label(wrap, text="التسجيل في الفعاليات", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text="اختر نوع المشاركة ثم اضف اسمك ثم اختر عدد الفعاليات وسجل",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(6, 18))

        # نوع المشاركة
        type_box = ttk.Frame(wrap, style="Content.TFrame")
        type_box.pack(fill="x", pady=(0, 8))

        self.participant_type = tk.StringVar(value="individual")

        ttk.Label(type_box, text="نوع المشاركة:", style="Sub.TLabel").pack(side="left", padx=(0, 12))

        ttk.Radiobutton(
            type_box, text="فردي", value="individual",
            variable=self.participant_type, command=self.refresh_lists
        ).pack(side="left", padx=6)

        ttk.Radiobutton(
            type_box, text="فرقة", value="team",
            variable=self.participant_type, command=self.refresh_lists
        ).pack(side="left", padx=6)

        self.mode_hint = ttk.Label(wrap, text="", style="Sub.TLabel")
        self.mode_hint.pack(anchor="w", pady=(0, 10))

        # إضافة اسم
        add_row = ttk.Frame(wrap, style="Content.TFrame")
        add_row.pack(fill="x", pady=(8, 8))

        self.add_label = ttk.Label(add_row, text="اكتب الاسم لإضافته:", style="Sub.TLabel")
        self.add_label.pack(side="left", padx=(0, 12))

        self.new_name_var = tk.StringVar()
        self.new_name_entry = ttk.Entry(add_row, textvariable=self.new_name_var, width=35)
        self.new_name_entry.pack(side="left")

        ttk.Button(
            add_row, text="إضافة", style="Primary.TButton",
            command=self.add_participant_name
        ).pack(side="left", padx=10)

        # اسم المشارك للتسجيل
        name_row = ttk.Frame(wrap, style="Content.TFrame")
        name_row.pack(fill="x", pady=8)

        ttk.Label(name_row, text="اسم المشارك للتسجيل:", style="Sub.TLabel").pack(side="left", padx=(0, 12))

        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(name_row, textvariable=self.name_var, width=42)
        self.name_entry.pack(side="left")

        # عدد الفعاليات
        count_row = ttk.Frame(wrap, style="Content.TFrame")
        count_row.pack(fill="x", pady=(12, 6))

        ttk.Label(count_row, text="عدد الفعاليات المطلوبة:", style="Sub.TLabel").pack(side="left", padx=(0, 12))

        self.want_count_combo = ttk.Combobox(count_row, values=[1, 2, 3, 4, 5], state="readonly", width=10)
        self.want_count_combo.pack(side="left")
        self.want_count_combo.set("1")

        self.count_hint = ttk.Label(wrap, text="اختياراتك: 0 / 1", style="Sub.TLabel")
        self.count_hint.pack(anchor="w", pady=(0, 6))

        # اختيار الفعاليات
        ttk.Label(wrap, text="اختر الفعاليات:", style="Sub.TLabel").pack(anchor="w", pady=(8, 6))

        list_frame = ttk.Frame(wrap, style="Content.TFrame")
        list_frame.pack(anchor="w", fill="x")

        self.events_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, width=52, height=9)
        self.events_listbox.pack(side="left")

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.events_listbox.yview)
        sb.pack(side="left", fill="y", padx=(6, 0))
        self.events_listbox.configure(yscrollcommand=sb.set)

        # زر التسجيل
        btn_row = ttk.Frame(wrap, style="Content.TFrame")
        btn_row.pack(fill="x", pady=(18, 0))
        ttk.Button(btn_row, text="تسجيل", style="Primary.TButton", command=self.do_register).pack(side="left")

        self.msg_label = ttk.Label(wrap, text="", style="Sub.TLabel")
        self.msg_label.pack(anchor="w", pady=(18, 0))

        self.refresh_lists()

    # ---------- helpers ----------
    def normalize_name(self, name: str) -> str:
        return " ".join(name.strip().split())

    def count_parts(self, name: str) -> int:
        return len([p for p in name.split(" ") if p])

    # ---------- add name ----------
    def add_participant_name(self):
        ptype = self.participant_type.get()
        new_name = self.normalize_name(self.new_name_var.get())

        if not new_name:
            messagebox.showerror("خطأ", "اكتب الاسم اولاً")
            return

        if ptype == "individual":
            if self.count_parts(new_name) != 4:
                messagebox.showerror("خطأ", "اسم الطالب لازم يكون رباعي")
                return
            if new_name in ds.individuals:
                messagebox.showwarning("موجود", "الاسم موجود مسبقا")
                return
            if len(ds.individuals) >= MAX_INDIVIDUALS:
                messagebox.showerror("ممنوع", f"وصلت للحد الاقصى للأفراد ({MAX_INDIVIDUALS})")
                return

            ds.individuals[new_name] = {"event_ids": []}
            ds.save_state()

        else:
            if self.count_parts(new_name) != 2:
                messagebox.showerror("خطأ", "اسم الفريق لازم يكون من كلمتين")
                return
            if new_name in ds.teams:
                messagebox.showwarning("موجود", "اسم الفريق موجود مسبقا")
                return
            if len(ds.teams) >= MAX_TEAMS:
                messagebox.showerror("ممنوع", f"وصلت للحد الاقصى للفرق ({MAX_TEAMS})")
                return

            ds.teams[new_name] = {"members": [], "event_ids": []}
            ds.save_state()

        self.new_name_var.set("")
        self.name_var.set(new_name)
        messagebox.showinfo("تم", f"تمت إضافة الاسم: {new_name}")

    # ---------- register ----------
    def do_register(self):
        ptype = self.participant_type.get()
        name = self.normalize_name(self.name_var.get())

        if not name:
            messagebox.showerror("خطأ", "اكتب اسمك أولاً")
            return

        wanted = int(self.want_count_combo.get())
        selected_indices = self.events_listbox.curselection()

        if len(selected_indices) != wanted:
            messagebox.showerror("خطأ", f"لازم تختار {wanted} فعالية")
            return

        selected_texts = [self.events_listbox.get(i) for i in selected_indices]
        selected_event_ids = [int(t.split("-")[0].strip()) for t in selected_texts]

        if ptype == "individual":
            existing = ds.individuals.get(name, {}).get("event_ids", [])
        else:
            existing = ds.teams.get(name, {}).get("event_ids", [])

        for eid in selected_event_ids:
            if eid in existing:
                messagebox.showerror("ممنوع", "مسجل مسبقا في نفس الفعالية")
                return

        if len(existing) + len(selected_event_ids) > MAX_EVENTS_PER_PARTICIPANT:
            messagebox.showerror("ممنوع", "تجاوزت الحد الاقصى 5 فعاليات")
            return

        new_events = existing + selected_event_ids

        if ptype == "individual":
            ds.register_individual(name, new_events)
        else:
            ds.register_team(name, [], new_events)

        self.msg_label.config(text=f"تم التسجيل ✅ {name} سجل {len(selected_event_ids)} فعالية")
        messagebox.showinfo("تم", "تم التسجيل بنجاح")

    # ---------- refresh ----------
    def refresh_lists(self):
        ptype = self.participant_type.get()

        self.events_listbox.delete(0, tk.END)
        filtered_events = [e for e in EVENTS if e["mode"] == ptype]
        for e in filtered_events:
            self.events_listbox.insert(tk.END, f"{e['id']} - {e['name']}")

        self.events_listbox.selection_clear(0, tk.END)
        self.want_count_combo.set("1")
        self.count_hint.config(text="اختياراتك: 0 / 1")