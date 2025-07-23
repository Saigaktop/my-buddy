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


async def update_last_seen(user_id: int, seen: dt.datetime | None = None) -> None:
    """Update or insert user's last seen timestamp."""
    seen = seen or dt.datetime.utcnow()
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO users(user_id, last_seen)
            VALUES(?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_seen=excluded.last_seen
            """,
            (user_id, seen.isoformat()),
        )
        await db.commit()


async def touch_user(user_id: int) -> None:
    await update_last_seen(user_id)


async def get_last_seen(user_id: int) -> dt.datetime | None:
    """Return last_seen for a user if present."""
    async with aiosqlite.connect(DB) as db:
        async with db.execute(
            "SELECT last_seen FROM users WHERE user_id=?",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
    if row and row[0]:
        return dt.datetime.fromisoformat(row[0])
    return None


async def get_all_users() -> list[tuple[int, dt.datetime, int]]:
    """Return all users with their last_seen and silence_hours."""
    async with aiosqlite.connect(DB) as db:
        async with db.execute(
            "SELECT user_id, last_seen, silence_hours FROM users"
        ) as cur:
            rows = await cur.fetchall()

    users = []
    for uid, seen, hours in rows:
        if seen:
            try:
                ts = dt.datetime.fromisoformat(seen)
            except ValueError:
                continue
            users.append((uid, ts, hours))
    return users


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
