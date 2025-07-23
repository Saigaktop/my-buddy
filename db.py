import aiosqlite
import datetime as dt
import asyncio

DB = "buddy.db"


async def init() -> None:
    async with aiosqlite.connect(DB) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                last_seen TEXT,
                silence_hours INTEGER DEFAULT 6
            );
            CREATE TABLE IF NOT EXISTS reminders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                due_at TEXT,
                interval_min INTEGER
            );
            """
        )
        await db.commit()


async def touch_user(user_id: int) -> None:
    """Update or insert user's last seen timestamp."""
    now = dt.datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO users(user_id, last_seen)
            VALUES(?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_seen=excluded.last_seen
            """,
            (user_id, now),
        )
        await db.commit()


async def add_reminder(
    user_id: int,
    text: str,
    due_at: dt.datetime,
    interval_min: int | None = None,
) -> None:
    """Insert a reminder for the user."""
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO reminders(user_id, text, due_at, interval_min) VALUES (?, ?, ?, ?)",
            (user_id, text, due_at.isoformat(), interval_min),
        )
        await db.commit()


asyncio.run(init())
