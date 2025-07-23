import aiosqlite, datetime as dt, os, asyncio
DB = "buddy.db"

async def init():
    async with aiosqlite.connect(DB) as db:
        await db.executescript("""
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
        """)
        await db.commit()

async def touch_user(user_id: int) -> None:
    """Update last_seen for a user or create the record."""
    now = dt.datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, last_seen)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_seen=excluded.last_seen
            """,
            (user_id, now),
        )
        await db.commit()

asyncio.run(init())
