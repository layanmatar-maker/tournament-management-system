# config.py

ADMIN_PASSWORD = "12345"
MAX_EVENTS_PER_PARTICIPANT = 5

MAX_TEAMS = 4
MAX_INDIVIDUALS = 20

# ألوان الثيم
THEME = {
    "BG": "#0f172a",
    "PANEL": "#111c33",
    "CARD": "#0b1224",
    "TEXT": "#e5e7eb",
    "MUTED": "#a3a3a3",
    "ACCENT": "#38bdf8",
    "OK": "#22c55e",
    "WARN": "#f59e0b",
}

# فعاليات: 6 للفرق + 6 للفردي
EVENTS = [
    # Team events (6)
    {"id": 1, "name": "كرة القدم", "mode": "team"},
    {"id": 2, "name": "كرة السلة", "mode": "team"},
    {"id": 3, "name": "تحدي برمجة جماعي", "mode": "team"},
    {"id": 4, "name": "مناظرة جماعية", "mode": "team"},
    {"id": 5, "name": "روبوتكس جماعي", "mode": "team"},
    {"id": 6, "name": "كويز ثقافي جماعي", "mode": "team"},

    # Individual events (6)
    {"id": 7, "name": "سباق 100 متر", "mode": "individual"},
    {"id": 8, "name": "تنس طاولة", "mode": "individual"},
    {"id": 9, "name": "مسابقة رياضيات", "mode": "individual"},
    {"id": 10, "name": "مسابقة علوم", "mode": "individual"},
    {"id": 11, "name": "شطرنج", "mode": "individual"},
    {"id": 12, "name": "كويز ثقافي فردي", "mode": "individual"},
]

# نظام النقاط لكل فعالية (للتعليمات)
EVENT_POINT_RULES = {
    # فرق - دوري
    1: {"type": "match", "win": 3, "draw": 1, "loss": 0},
    2: {"type": "match", "win": 3, "draw": 1, "loss": 0},

    # فرق - تقييم
    3: {"type": "rubric", "max": 20, "rubric": [("صحة الحل", 10), ("السرعة", 5), ("تنظيم الكود", 5)]},
    4: {"type": "rubric", "max": 15, "rubric": [("قوة الحجة", 6), ("تنظيم الحديث", 5), ("الالتزام بالوقت", 4)]},
    5: {"type": "rubric", "max": 20, "rubric": [("انجاز المهام", 12), ("اخطاء أقل", 4), ("زمن أقل", 4)]},

    # فرق - نقاط مباشرة
    6: {"type": "score", "unit": "اجابة صحيحة", "per": 1},

    # فردي
    7: {"type": "rank", "places": {1: 10, 2: 7, 3: 5}, "participation": 1},
    8: {"type": "match", "win": 3, "draw": 1, "loss": 0},
    9: {"type": "score", "max": 20, "unit": "درجة"},
    10: {"type": "score", "max": 20, "unit": "درجة"},
    11: {"type": "match", "win": 1, "draw": 0.5, "loss": 0},
    12: {"type": "score", "unit": "اجابة صحيحة", "per": 1},
}
ADMIN_PASSWORD = "12345"

MAX_EVENTS_PER_PARTICIPANT = 5
MAX_TEAMS = 4
MAX_INDIVIDUALS = 20

THEME = {
    "BG": "#0f172a",
    "PANEL": "#111c33",
    "CARD": "#0b1224",
    "TEXT": "#e5e7eb",
    "MUTED": "#a3a3a3",
    "ACCENT": "#38bdf8",
    "OK": "#22c55e",
    "WARN": "#f59e0b",
}