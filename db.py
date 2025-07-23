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

asyncio.run(init())
