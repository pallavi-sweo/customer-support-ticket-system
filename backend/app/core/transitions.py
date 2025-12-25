from typing import Final

# Strict lifecycle transitions
ALLOWED_TRANSITIONS: Final[dict[str, set[str]]] = {
    "OPEN": {"IN_PROGRESS", "CLOSED"},
    "IN_PROGRESS": {"RESOLVED", "CLOSED"},
    "RESOLVED": {"CLOSED"},
    "CLOSED": set(),
}


def validate_transition(old_status: str, new_status: str) -> None:
    if new_status == old_status:
        return

    allowed = ALLOWED_TRANSITIONS.get(old_status)
    if allowed is None:
        raise ValueError(f"Unknown current status: {old_status}")

    if new_status not in allowed:
        raise ValueError(f"Invalid transition {old_status} -> {new_status}")
