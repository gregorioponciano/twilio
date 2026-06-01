from typing import List, Optional

from src.database import Database
from src.models import AVAILABLE_COLORS, CallLog, Contact, Message


class ContactRepository:
    def __init__(self) -> None:
        self.db = Database()

    def list_all(self) -> List[Contact]:
        conn = self.db.get_conn()
        rows = conn.execute(
            "SELECT * FROM contacts ORDER BY name ASC"
        ).fetchall()
        return [self._row_to_contact(r) for r in rows]

    def search(self, query: str) -> List[Contact]:
        conn = self.db.get_conn()
        pattern = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? ORDER BY name ASC",
            (pattern, pattern),
        ).fetchall()
        return [self._row_to_contact(r) for r in rows]

    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        conn = self.db.get_conn()
        row = conn.execute(
            "SELECT * FROM contacts WHERE id = ?", (contact_id,)
        ).fetchone()
        return self._row_to_contact(row) if row else None

    def get_by_phone(self, phone: str) -> Optional[Contact]:
        conn = self.db.get_conn()
        row = conn.execute(
            "SELECT * FROM contacts WHERE phone = ?", (phone,)
        ).fetchone()
        return self._row_to_contact(row) if row else None

    def save(self, contact: Contact) -> Contact:
        conn = self.db.get_conn()
        if contact.id:
            conn.execute(
                "UPDATE contacts SET name=?, phone=?, avatar_color=?, "
                "updated_at=datetime('now','localtime') WHERE id=?",
                (contact.name, contact.phone, contact.avatar_color, contact.id),
            )
        else:
            if not contact.avatar_color:
                contact.avatar_color = AVAILABLE_COLORS[
                    hash(contact.phone) % len(AVAILABLE_COLORS)
                ]
            cursor = conn.execute(
                "INSERT INTO contacts (name, phone, avatar_color) VALUES (?, ?, ?)",
                (contact.name, contact.phone, contact.avatar_color),
            )
            contact.id = cursor.lastrowid
        conn.commit()
        return contact

    def delete(self, contact_id: int) -> None:
        conn = self.db.get_conn()
        conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()

    def _row_to_contact(self, row) -> Contact:
        return Contact(
            id=row["id"],
            name=row["name"],
            phone=row["phone"],
            avatar_color=row["avatar_color"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class MessageRepository:
    def __init__(self) -> None:
        self.db = Database()

    def list_by_contact(self, contact_id: int, limit: int = 100) -> List[Message]:
        conn = self.db.get_conn()
        rows = conn.execute(
            "SELECT * FROM messages WHERE contact_id = ? "
            "ORDER BY created_at ASC LIMIT ?",
            (contact_id, limit),
        ).fetchall()
        return [self._row_to_message(r) for r in rows]

    def last_for_contact(self, contact_id: int) -> Optional[Message]:
        conn = self.db.get_conn()
        row = conn.execute(
            "SELECT * FROM messages WHERE contact_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (contact_id,),
        ).fetchone()
        return self._row_to_message(row) if row else None

    def last_for_each_contact(self) -> dict:
        conn = self.db.get_conn()
        rows = conn.execute("""
            SELECT m.* FROM messages m
            INNER JOIN (
                SELECT contact_id, MAX(created_at) AS max_created
                FROM messages GROUP BY contact_id
            ) latest ON m.contact_id = latest.contact_id
            AND m.created_at = latest.max_created
            ORDER BY m.created_at DESC
        """).fetchall()
        return {r["contact_id"]: self._row_to_message(r) for r in rows}

    def save(self, message: Message) -> Message:
        conn = self.db.get_conn()
        if not message.id:
            cursor = conn.execute(
                "INSERT INTO messages (contact_id, direction, content, channel, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (message.contact_id, message.direction, message.content,
                 message.channel, message.status),
            )
            message.id = cursor.lastrowid
            conn.commit()
        return message

    def delete_by_contact(self, contact_id: int) -> None:
        conn = self.db.get_conn()
        conn.execute("DELETE FROM messages WHERE contact_id = ?", (contact_id,))
        conn.commit()

    def _row_to_message(self, row) -> Message:
        return Message(
            id=row["id"],
            contact_id=row["contact_id"],
            direction=row["direction"],
            content=row["content"],
            channel=row["channel"],
            status=row["status"],
            created_at=row["created_at"],
        )


class CallLogRepository:
    def __init__(self) -> None:
        self.db = Database()

    def list_by_contact(self, contact_id: int) -> List[CallLog]:
        conn = self.db.get_conn()
        rows = conn.execute(
            "SELECT * FROM call_logs WHERE contact_id = ? "
            "ORDER BY created_at DESC",
            (contact_id,),
        ).fetchall()
        return [self._row_to_call_log(r) for r in rows]

    def list_all(self, limit: int = 50) -> List[CallLog]:
        conn = self.db.get_conn()
        rows = conn.execute(
            "SELECT * FROM call_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_call_log(r) for r in rows]

    def save(self, call_log: CallLog) -> CallLog:
        conn = self.db.get_conn()
        if not call_log.id:
            cursor = conn.execute(
                "INSERT INTO call_logs (contact_id, direction, duration, status) "
                "VALUES (?, ?, ?, ?)",
                (call_log.contact_id, call_log.direction, call_log.duration, call_log.status),
            )
            call_log.id = cursor.lastrowid
            conn.commit()
        return call_log

    def delete_by_contact(self, contact_id: int) -> None:
        conn = self.db.get_conn()
        conn.execute("DELETE FROM call_logs WHERE contact_id = ?", (contact_id,))
        conn.commit()

    def _row_to_call_log(self, row) -> CallLog:
        return CallLog(
            id=row["id"],
            contact_id=row["contact_id"],
            direction=row["direction"],
            duration=row["duration"],
            status=row["status"],
            created_at=row["created_at"],
        )
