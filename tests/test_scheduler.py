import asyncio
import datetime as dt
from unittest.mock import AsyncMock

import aiosqlite

import pytest

import db
import scheduler


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))


class FakeApp:
    def __init__(self, bot):
        self.bot = bot


MEM_DB = ":memory:"


@pytest.fixture(autouse=True)
def memory_db(monkeypatch):
    """Use an in-memory database for tests."""

    async def open_conn():
        return await aiosqlite.connect(MEM_DB)

    conn = asyncio.run(open_conn())

    class ConnWrapper:
        def __init__(self, conn):
            self._conn = conn

        async def __aenter__(self):
            return self._conn

        async def __aexit__(self, exc_type, exc, tb):
            pass

    def connect_patch(*args, **kwargs):
        return ConnWrapper(conn)

    monkeypatch.setattr(db, "DB", MEM_DB)
    monkeypatch.setattr(db.aiosqlite, "connect", connect_patch)
    monkeypatch.setattr(scheduler.aiosqlite, "connect", connect_patch)

    asyncio.run(db.init_db())

    yield

    asyncio.run(conn.close())


def test_reminder_delivery(monkeypatch):
    bot = FakeBot()
    app = FakeApp(bot)

    user_id = 42
    asyncio.run(db.touch_user(user_id))
    due = dt.datetime.utcnow() - dt.timedelta(minutes=1)
    asyncio.run(db.add_reminder(user_id, "ping", due))

    asyncio.run(scheduler.tick(app))

    assert bot.sent == [(user_id, "ping")]
    async def get_count():
        async with aiosqlite.connect(MEM_DB, uri=True) as con:
            async with con.execute("SELECT COUNT(*) FROM reminders") as cur:
                return (await cur.fetchone())[0]

    count = asyncio.run(get_count())
    assert count == 0


def test_silence_triggers_fact(monkeypatch):
    bot = FakeBot()
    app = FakeApp(bot)

    user_id = 99
    silent_time = dt.datetime.utcnow() - dt.timedelta(hours=10)
    asyncio.run(db.update_last_seen(user_id, silent_time))

    monkeypatch.setattr(scheduler, "fetch_trending_fact", AsyncMock(return_value="fact"))
    monkeypatch.setattr(scheduler, "gpt_short", AsyncMock(return_value="short"))

    asyncio.run(scheduler.tick(app))

    assert bot.sent
    chat_id, text = bot.sent[0]
    assert chat_id == user_id
    assert "short" in text

    now = dt.datetime.utcnow()
    seen = asyncio.run(db.get_last_seen(user_id))
    assert now - seen < dt.timedelta(seconds=5)
