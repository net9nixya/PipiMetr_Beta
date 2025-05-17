import asyncio
import random
import sqlite3
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Command
from config import BOT_TOKEN, MAX_LEVEL
from keyboard import start_private_keyboard, top_keyboard, submit_idea_keyboard, tea_top_keyboard

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)
DB_PATH = "tea.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tea (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            size REAL DEFAULT 0,
            total_growth REAL DEFAULT 0,
            last_used TEXT,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def can_grow(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT last_used FROM tea WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row or not row[0]:
        return True
    last_used = datetime.fromisoformat(row[0])
    return datetime.now() - last_used >= timedelta(hours=1)

def get_luck_multiplier(level: int) -> float:
    return min(1.0 + level * 0.02, 1.2)

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, size, total_growth, last_used, level, exp FROM tea WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_growth(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT level, exp, size, total_growth FROM tea WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if not row:
        level = 1
        exp = 0
        size = 0
        total = 0
    else:
        level, exp, size, total = row

    luck = get_luck_multiplier(level)
    growth = round(random.uniform(0.5, 1.2) * luck, 2)
    new_size = round(size + growth, 2)
    new_total = round(total + growth, 2)
    new_exp = exp + 1

    new_level = level
    if new_exp >= level * 5 and level < MAX_LEVEL:
        new_level += 1
        new_exp = 0

    now = datetime.now().isoformat()
    c.execute('''
        INSERT INTO tea (user_id, username, size, total_growth, last_used, level, exp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            size = ?,
            total_growth = ?,
            last_used = ?,
            level = ?,
            exp = ?
    ''', (user_id, username, new_size, new_total, now, new_level, new_exp,
          new_size, new_total, now, new_level, new_exp))
    conn.commit()
    conn.close()
    return growth, new_size, new_level

@dp.message_handler(commands=["start_tea", "start_tea@PipiMetrBot"])
async def cmd_start(message: types.Message):
    if message.chat.type == "private":
        await message.answer(
            "Привет! Чайометр — весёлый бот для чатов, который помогает измерять прогресс!\n\n"
            "Раз в час игрок может использовать команду /drink, чтобы выпить чаю 🍵\n\n"
            "Мои команды — /info_tea",
            reply_markup=start_private_keyboard
        )
    else:
        await message.answer("Бот активен! Используйте /drink чтобы начать игру!")

@dp.message_handler(commands=["info_tea", "help_tea", "info_tea@PipiMetrBot", "help_tea@PipiMetrBot"])
async def cmd_info(message: types.Message):
    await message.answer(
        "Команды бота:\n"
        "/start_tea — запустить бота\n"
        "/drink — начать игру\n"
        "/me_tea — профиль\n"
        "/stats_tea — статистика группы\n"
        "/top_tea — топ игроков и чатов\n"
        "/help_tea — помощь по боту",
        reply_markup=submit_idea_keyboard
    )

@dp.message_handler(commands=["drink", "drink@PipiMetrBot"])
async def cmd_dick(message: types.Message):
    if message.chat.type == "private":
        await message.answer("Эта команда работает только в группах. Добавь меня в чат!")
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    if can_grow(user_id):
        growth, new_size, level = update_growth(user_id, username)
        await message.reply(
            f"🧋 <b>{username}</b>, ты выпил <b>{growth} л.</b>!\n"
            f"🍵 Всего: <b>{new_size} л.</b>\n"
            f"🎖 Уровень: <b>{level}</b>"
        )
    else:
        row = get_user(user_id)
        if row:
            username, size, *_ = row
            await message.reply(
                f"⏳ Эй, не спеши! Ты уже пил недавно.\n"
                f"Текущий результат: <b>{size} л.</b> 🍵"
            )
        else:
            await message.reply("Ты ещё не начал игру! Используй /dick")

@dp.message_handler(commands=["me_tea", "me_tea@PipiMetrBot", "profile_tea", "profile_tea@PipiMetrBot"])
async def cmd_me(message: types.Message):
    row = get_user(message.from_user.id)
    if row:
        username, size, total, last, level, exp = row
        if last:
            delta = datetime.now() - datetime.fromisoformat(last)
            wait = max(0, 3600 - int(delta.total_seconds()))
            minutes = wait // 60
            seconds = wait % 60
            timer = f"{minutes} мин. {seconds} сек."
        else:
            timer = "Можно прямо сейчас!"

        await message.answer(
            f"🧋 Профиль\n"
            f"👤 {username}\n\n"
            f"📈 Сегодня: {round(size, 2)} л.\n"
            f"🍵 Всего: {round(total, 2)} л.\n"
            f"🎖 Уровень: {level} ({exp} опыта)\n"
            f"⏰ Следующее выпивание через: {timer}"
        )
    else:
        await message.answer("Ты ещё не начал игру! Напиши /drink")

@dp.message_handler(commands=["stats_tea", "stats_tea@PipiMetrBot"])
async def cmd_stats(message: types.Message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, total_growth FROM pipi ORDER BY total_growth DESC LIMIT 10")
    top = c.fetchall()
    conn.close()

    if top:
        text = "📊 Топ 10 игроков чата:\n\n"
        for i, (user, growth) in enumerate(top, 1):
            text += f"{i}. {user} — {round(growth, 2)} см\n"
        text += "\nТОП лучших игроков — /top"
    else:
        text = "Нет данных. Используй /drink, чтобы начать игру!"

    await message.answer(text)

@dp.message_handler(commands=["top_tea", "top_tea@PipiMetrBot"])
async def cmd_top(message: types.Message):
    await message.answer("🧋 ТОП лучших игроков и чатов (В разработке: @Project_X)", reply_markup=tea_top_keyboard)

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
