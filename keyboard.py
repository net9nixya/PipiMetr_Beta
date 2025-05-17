from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
start_private_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить ПипиМетр в чатик", url="https://t.me/PipiMetrBot?startgroup=true")]
])
top_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍆 Посмотреть топ игроков", callback_data="top_players")],
    [InlineKeyboardButton(text="💬 Посмотреть топ чатов", callback_data="top_chats")]
])
