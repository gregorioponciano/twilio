from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Contact:
    id: int = 0
    name: str = ""
    phone: str = ""
    avatar_color: str = "#128C7E"
    created_at: str = ""
    updated_at: str = ""

    @property
    def initials(self) -> str:
        parts = self.name.strip().split()
        if not parts:
            return "?"
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return parts[0][0].upper()

    @property
    def last_message_preview(self) -> str:
        return ""


@dataclass
class Message:
    id: int = 0
    contact_id: int = 0
    direction: str = "sent"
    content: str = ""
    channel: str = "sms"
    status: str = "sent"
    created_at: str = ""

    @property
    def is_sent(self) -> bool:
        return self.direction == "sent"

    @property
    def time_display(self) -> str:
        try:
            dt = datetime.fromisoformat(self.created_at)
            return dt.strftime("%H:%M")
        except (ValueError, TypeError):
            return ""


@dataclass
class CallLog:
    id: int = 0
    contact_id: int = 0
    direction: str = "outgoing"
    duration: int = 0
    status: str = "completed"
    created_at: str = ""

    @property
    def duration_display(self) -> str:
        if self.status == "missed":
            return ""
        mins, secs = divmod(self.duration, 60)
        if mins > 0:
            return f"{mins}:{secs:02d} min"
        return f"{secs}s"

    @property
    def time_display(self) -> str:
        try:
            dt = datetime.fromisoformat(self.created_at)
            return dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            return ""


AVAILABLE_COLORS = [
    "#128C7E", "#25D366", "#34B7F1", "#E91E63", "#9C27B0",
    "#673AB7", "#3F51B5", "#2196F3", "#00BCD4", "#009688",
    "#4CAF50", "#FF9800", "#FF5722", "#795548", "#607D8B",
]
