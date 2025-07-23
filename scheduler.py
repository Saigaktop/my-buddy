from __future__ import annotations
import datetime as dt, os, aiosqlite
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from prompts import SYSTEM_PROMPT
from openai import AsyncOpenAI          # ⬅ новый импорт
from telegram.ext import Application          # ← импортируем класс
from telegram.ext import ContextTypes         # ← он вам пригодится дальше

client = AsyncOpenAI(                  # ⬅ создаём клиента
    api_key=os.getenv("OPENAI_API_KEY")
)

# модель OpenAI можно задать через переменную среды
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

async def gpt_short(message: str) -> str:
    chat = await client.chat.completions.create(
        model=OPENAI_MODEL,           # можно заменить на любую доступную модель
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": message},
        ],
    )
    return chat.choices[0].message.content

async def tick(app: Application):
    now_utc = dt.datetime.utcnow()

    async with aiosqlite.connect("buddy.db") as db:
        async with db.execute(
            "SELECT id,user_id,text,due_at,interval_min FROM reminders"
        ) as cur:
            reminders = await cur.fetchall()

        for rid, uid, text, due_iso, interval in reminders:
            due = dt.datetime.fromisoformat(due_iso)

            if now_utc >= due:
                # шлём сообщение
                await app.bot.send_message(uid, text)

                if interval:  # повтор
                    new_due = due + dt.timedelta(minutes=interval)
                    await db.execute(
                        "UPDATE reminders SET due_at=? WHERE id=?",
                        (new_due.isoformat(), rid)
                    )
                else:         # одноразовое
                    await db.execute(
                        "DELETE FROM reminders WHERE id=?", (rid,)
                    )
        await db.commit()




def start_scheduler(app):
    sched = AsyncIOScheduler()
    sched.add_job(tick,'interval',minutes=1,args=[app])
    sched.start()
