# utils.py

from config import EVENTS

def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())

def count_parts(name: str) -> int:
    return len([p for p in name.split(" ") if p])

def get_event_by_id(eid: int):
    for e in EVENTS:
        if e["id"] == eid:
            return e
    return None

def get_events_for_mode(mode: str):
    return [e for e in EVENTS if e["mode"] == mode]

def get_registered_participants_for_event(event_id: int, event_registrations: dict):
    return sorted(event_registrations.get(event_id, []))