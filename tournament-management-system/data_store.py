# data_store.py
from __future__ import annotations
import json
import os
from typing import Dict, List, Any
from datetime import datetime

DATA_FILE = "tournament_data.json"


def _default_state() -> Dict[str, Any]:
    return {
        # registrations
        "teams": {},
        "individuals": {},
        "participant_events": {},
        "event_registrations": [],

        # scores
        "event_scores": {},

        # publish flags
        "PUBLISH_POINTS": False,
        "PUBLISH_LEADERBOARD": False,

        # ✅ admins chat (NEW)
        "admin_chat": [],  # [{"from": "Admin 1", "ts": "2026-03-04 22:10", "text": "..."}]
    }


teams: Dict[str, Any] = {}
individuals: Dict[str, Any] = {}
participant_events: Dict[str, Any] = {}
event_registrations: List[Dict[str, Any]] = []

event_scores: Dict[str, Any] = {}

PUBLISH_POINTS: bool = False
PUBLISH_LEADERBOARD: bool = False

# ✅ admins chat globals (NEW)
admin_chat: List[Dict[str, Any]] = []


def load_state() -> None:
    global teams, individuals, participant_events, event_registrations
    global event_scores, PUBLISH_POINTS, PUBLISH_LEADERBOARD
    global admin_chat

    if not os.path.exists(DATA_FILE):
        state = _default_state()
        _apply_state(state)
        save_state()
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = _default_state()

    # ensure required keys exist
    base = _default_state()
    for k, v in base.items():
        if k not in state:
            state[k] = v

    _apply_state(state)


def save_state() -> None:
    state = {
        "teams": teams,
        "individuals": individuals,
        "participant_events": participant_events,
        "event_registrations": event_registrations,

        "event_scores": event_scores,

        "PUBLISH_POINTS": PUBLISH_POINTS,
        "PUBLISH_LEADERBOARD": PUBLISH_LEADERBOARD,

        # ✅ chat
        "admin_chat": admin_chat,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _apply_state(state: Dict[str, Any]) -> None:
    global teams, individuals, participant_events, event_registrations
    global event_scores, PUBLISH_POINTS, PUBLISH_LEADERBOARD
    global admin_chat

    teams = state.get("teams", {}) or {}
    individuals = state.get("individuals", {}) or {}
    participant_events = state.get("participant_events", {}) or {}
    event_registrations = state.get("event_registrations", []) or []

    event_scores = state.get("event_scores", {}) or {}

    PUBLISH_POINTS = bool(state.get("PUBLISH_POINTS", False))
    PUBLISH_LEADERBOARD = bool(state.get("PUBLISH_LEADERBOARD", False))

    admin_chat = state.get("admin_chat", []) or []


# auto-load
load_state()


def _participant_key(ptype: str, name: str) -> str:
    ptype = "team" if ptype == "team" else "individual"
    return f"{ptype}:{name.strip()}"


def register_individual(person_name: str, event_ids: List[int]) -> None:
    person_name = person_name.strip()
    event_ids = list(dict.fromkeys(event_ids))
    if not person_name:
        return

    individuals[person_name] = {"event_ids": event_ids}

    key = _participant_key("individual", person_name)
    participant_events[key] = {"type": "individual", "name": person_name, "event_ids": event_ids}

    _rebuild_event_registrations_for(key)
    save_state()


def register_team(team_name: str, members: List[str], event_ids: List[int]) -> None:
    team_name = team_name.strip()
    clean_members = [m.strip() for m in members if m.strip()]
    event_ids = list(dict.fromkeys(event_ids))
    if not team_name:
        return

    teams[team_name] = {"members": clean_members, "event_ids": event_ids}

    key = _participant_key("team", team_name)
    participant_events[key] = {
        "type": "team",
        "name": team_name,
        "members": clean_members,
        "event_ids": event_ids,
    }

    _rebuild_event_registrations_for(key)
    save_state()


def _rebuild_event_registrations_for(participant_key: str) -> None:
    global event_registrations

    event_registrations = [
        r for r in event_registrations
        if _participant_key(r.get("type", ""), r.get("name", "")) != participant_key
    ]

    pe = participant_events.get(participant_key)
    if not pe:
        return

    ptype = pe["type"]
    name = pe["name"]
    for eid in pe.get("event_ids", []):
        event_registrations.append({"type": ptype, "name": name, "event_id": int(eid)})


def list_participants() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for _key, pe in (participant_events or {}).items():
        row = {
            "type": pe.get("type", "individual"),
            "name": pe.get("name", ""),
            "event_ids": pe.get("event_ids", []),
        }
        if pe.get("type") == "team":
            row["members"] = pe.get("members", [])
        out.append(row)

    out.sort(key=lambda x: (x["type"], x["name"]))
    return out


def set_flag_points(value: bool) -> None:
    global PUBLISH_POINTS
    PUBLISH_POINTS = bool(value)
    save_state()


def set_flag_leaderboard(value: bool) -> None:
    global PUBLISH_LEADERBOARD
    PUBLISH_LEADERBOARD = bool(value)
    save_state()


def add_score(ptype: str, name: str, event_id: int, score: float) -> None:
    global event_scores
    ptype = "team" if ptype == "team" else "individual"
    name = name.strip()

    key = _participant_key(ptype, name)
    if key not in event_scores:
        event_scores[key] = {}

    event_scores[key][str(int(event_id))] = float(score)
    save_state()


def delete_all_scores() -> None:
    global event_scores
    event_scores = {}
    save_state()


def get_scores_table(method: str = "avg") -> List[Dict[str, Any]]:
    """
    method:
      - "avg" => نظام A (الأعدل): ترتيب حسب المتوسط
      - "total" => ترتيب حسب المجموع
    """
    rows: List[Dict[str, Any]] = []
    for key, details in (event_scores or {}).items():
        if ":" in key:
            ptype, name = key.split(":", 1)
        else:
            ptype, name = "individual", key

        total = 0.0
        count = 0
        fixed: Dict[str, float] = {}

        for eid_str, sc in (details or {}).items():
            try:
                val = float(sc)
            except Exception:
                val = 0.0
            fixed[str(eid_str)] = val
            total += val
            count += 1

        avg = (total / count) if count > 0 else 0.0
        rows.append({
            "type": ptype,
            "name": name,
            "total": total,
            "avg": avg,
            "events_count": count,
            "details": fixed,
        })

    if method == "total":
        rows.sort(key=lambda r: r["total"], reverse=True)
    else:
        rows.sort(key=lambda r: (r["avg"], r["total"]), reverse=True)

    return rows


# =========================================================
# ✅ Admin Chat API (NEW)
# =========================================================
def get_admin_chat() -> List[Dict[str, Any]]:
    """يرجع كل رسائل النقاش."""
    load_state()
    return list(admin_chat or [])


def add_admin_message(sender: str, text: str) -> None:
    """يضيف رسالة جديدة للنقاش."""
    global admin_chat
    sender = (sender or "Admin").strip()
    text = (text or "").strip()
    if not text:
        return

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    admin_chat.append({"from": sender, "ts": ts, "text": text})

    # optional: keep it light (last 300 msgs)
    if len(admin_chat) > 300:
        admin_chat = admin_chat[-300:]

    save_state()


def clear_admin_chat() -> None:
    """يمسح كل النقاش."""
    global admin_chat
    admin_chat = []
    save_state()

from openpyxl import Workbook


def export_to_excel(file_name="tournament_results.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    ws.append(["Type", "Name", "Event ID", "Score"])

    for key, details in event_scores.items():

        if ":" in key:
            ptype, name = key.split(":", 1)
        else:
            ptype, name = "individual", key

        for eid, score in details.items():
            ws.append([ptype, name, eid, score])

    wb.save(file_name)    