# pages_instructions.py
import tkinter as tk
from tkinter import ttk
from config import EVENTS, EVENT_POINT_RULES, MAX_EVENTS_PER_PARTICIPANT, MAX_INDIVIDUALS, MAX_TEAMS


class InstructionsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app

        wrap = ttk.Frame(self, style="Content.TFrame")
        wrap.pack(fill="both", expand=True, padx=30, pady=30)

        ttk.Label(wrap, text="التعليمات", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text="شرح الفعاليات وقوانين التسجيل وطريقة احتساب النقاط والتحكيم",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(6, 14))

        nb = ttk.Notebook(wrap)
        nb.pack(fill="both", expand=True)

        tab_general = ttk.Frame(nb)
        tab_ind = ttk.Frame(nb)
        tab_team = ttk.Frame(nb)

        nb.add(tab_general, text="قوانين عامة")
        nb.add(tab_ind, text="فعاليات فردية")
        nb.add(tab_team, text="فعاليات الفرق")

        self._build_general(tab_general)
        self._build_events(tab_ind, mode="individual")
        self._build_events(tab_team, mode="team")

    # =========================
    # تنسيق نظام النقاط
    # =========================
    def _format_points(self, event_id: int) -> str:
        rule = EVENT_POINT_RULES.get(event_id)
        if not rule:
            return "سيتم تحديد نظام النقاط لاحقا"

        t = rule.get("type")

        if t == "match":
            return f"فوز = {rule['win']} | تعادل = {rule['draw']} | خسارة = {rule['loss']}"

        if t == "rank":
            places = rule.get("places", {})
            parts = [f"المركز {p} = {places[p]}" for p in sorted(places.keys())]
            if "participation" in rule:
                parts.append(f"مشاركة = {rule['participation']}")
            return " | ".join(parts)

        if t == "score":
            if "per" in rule:
                return f"كل {rule.get('unit','وحدة')} = {rule['per']} نقطة"
            if "max" in rule:
                return f"النقاط حسب {rule.get('unit','الدرجة')} (حد اقصى {rule['max']})"
            return "النقاط حسب المجموع"

        if t == "rubric":
            rb = rule.get("rubric", [])
            txt = " + ".join([f"{name}({pts})" for name, pts in rb])
            mx = rule.get("max", "")
            return f"تقييم: {txt}" + (f" (المجموع {mx})" if mx != "" else "")

        return "نظام نقاط غير معروف"

    # =========================
    # كارد UI
    # =========================
    def _card(self, parent, title: str, lines: list, accent=None):
        card = ttk.Frame(parent, style="Card.TFrame")
        bar = tk.Frame(card, bg=(accent or self.app.COL_ACCENT), height=6)
        bar.pack(fill="x")

        body = ttk.Frame(card, style="Card.TFrame")
        body.pack(fill="both", expand=True, padx=14, pady=14)

        ttk.Label(body, text=title, style="CardTitle.TLabel").pack(anchor="w")
        for ln in lines:
            ttk.Label(
                body,
                text="• " + ln,
                style="CardText.TLabel",
                wraplength=820,
                justify="left",
            ).pack(anchor="w", pady=(6, 0))
        return card

    # =========================
    # سكرول محترم للتاب
    # =========================
    def _scroll_area(self, parent):
        outer = ttk.Frame(parent)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=self.app.COL_BG, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        sb.pack(side="left", fill="y")
        canvas.configure(yscrollcommand=sb.set)

        inner = ttk.Frame(canvas)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(_=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_resize(event):
            canvas.itemconfig(win, width=event.width)

        inner.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_resize)

        # ✅ سكرول ثابت حتى لو الماوس فوق عناصر داخلية
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        def _bind_wheel(_):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)
        inner.bind("<Enter>", _bind_wheel)
        inner.bind("<Leave>", _unbind_wheel)

        return inner

    # =========================
    # تبويب القوانين العامة
    # =========================
    def _build_general(self, parent):
        inner = self._scroll_area(parent)

        self._card(
            inner,
            "قوانين التسجيل",
            [
                "التسجيل متاح للأفراد والفرق حسب نوع الفعالية",
                f"كل مشارك يختار من 1 إلى {MAX_EVENTS_PER_PARTICIPANT} فعاليات فقط",
                "ممنوع تكرار نفس الفعالية لنفس المشارك",
                f"حد أقصى للأفراد {MAX_INDIVIDUALS}",
                f"حد أقصى للفرق {MAX_TEAMS}",
                "الفردي لازم اسم رباعي والفرقة لازم اسم من مقطعين",
            ],
            accent=self.app.COL_ACCENT,
        ).pack(fill="x", pady=(0, 12))

        self._card(
            inner,
            "نظام النقاط بشكل عام",
            [
                "كل فعالية لها نظام نقاط مختلف حسب طبيعتها",
                "فعاليات فوز/تعادل/خسارة: النتيجة تتحول لنقاط",
                "فعاليات التقييم: المشرف يعطي نقاط حسب معايير محددة (Rubric)",
                "فعاليات المراكز: نقاط حسب المركز الاول والثاني والثالث + مشاركة",
                "يتم اعتماد النتيجة من اللجنة قبل نشر النقاط للطلاب",
            ],
            accent=self.app.COL_WARN,
        ).pack(fill="x", pady=(0, 12))

        self._card(
            inner,
            "طريقة التحكيم وتسجيل النتائج",
            [
                "يتم تعيين مشرف او لجنة لكل فعالية",
                "يتم تسجيل النتائج بعد انتهاء الفعالية مباشرة",
                "فعاليات الدوري تعتمد على فوز تعادل خسارة ثم تتحول لنقاط",
                "فعاليات التقييم تعتمد على معايير واضحة",
                "قرار اللجنة نهائي بعد اعتماد النتيجة",
            ],
            accent=self.app.COL_OK,
        ).pack(fill="x", pady=(0, 12))

    # =========================
    # نصوص افتراضية لكل لعبة
    # =========================
    def _default_event_text(self):
        return {
            1: {"play": "مباريات بين الفرق حسب جدول البطولة", "rules": "التزام بالوقت والروح الرياضية"},
            2: {"play": "مباراة كرة سلة حسب الوقت المحدد", "rules": "اتباع تعليمات الحكم"},
            3: {"play": "تحدي برمجة ضمن وقت محدد", "rules": "ممنوع النسخ او الغش"},
            4: {"play": "مناظرة بين فريقين حول موضوع محدد", "rules": "ممنوع المقاطعة واحترام الطرف الآخر"},
            5: {"play": "مهمة روبوتكس حسب التحدي المتوفر", "rules": "سلامة أولا"},
            6: {"play": "كويز ثقافي للفرق بجولات", "rules": "ممنوع استخدام الهاتف"},
            7: {"play": "سباق 100 متر الأسرع زمن يفوز", "rules": "الانطلاق عند الاشارة فقط"},
            8: {"play": "تنس طاولة فردي بنظام مباريات", "rules": "قوانين الإرسال واللعب النظيف"},
            9: {"play": "مسابقة رياضيات ضمن وقت", "rules": "حسب تعليمات المراقب"},
            10: {"play": "مسابقة علوم", "rules": "الالتزام بإرشادات السلامة"},
            11: {"play": "شطرنج فردي بنظام مباريات", "rules": "احترام الوقت"},
            12: {"play": "كويز ثقافي فردي", "rules": "ممنوع المساعدة او الغش"},
        }

    # =========================
    # تبويب الفعاليات (فردي/فرق)
    # =========================
    def _build_events(self, parent, mode: str):
        inner = self._scroll_area(parent)
        text_map = self._default_event_text()

        header = "الفعاليات الفردية" if mode == "individual" else "فعاليات الفرق"
        accent = self.app.COL_OK if mode == "individual" else self.app.COL_WARN

        self._card(
            inner,
            header,
            [
                "اقرأ شرح كل فعالية تحت",
                "نظام النقاط يظهر لكل فعالية بشكل واضح",
            ],
            accent=accent,
        ).pack(fill="x", pady=(0, 12))

        for ev in [e for e in EVENTS if e["mode"] == mode]:
            info = text_map.get(ev["id"], {})
            lines = [
                f"طريقة اللعب: {info.get('play','')}",
                f"نظام النقاط: {self._format_points(ev['id'])}",
                f"قوانين: {info.get('rules','')}",
            ]
            self._card(inner, f"{ev['id']} - {ev['name']}", lines, accent=self.app.COL_ACCENT).pack(
                fill="x", pady=(0, 12)
            )