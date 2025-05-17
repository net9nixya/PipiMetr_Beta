from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
start_private_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить ПипиМетр в чатик", url="https://t.me/PipiMetrBot?startgroup=true")],
    [InlineKeyboardButton(text="💡 Предложить идею", url="https://t.me/Project_X")]
])
top_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍆 Посмотреть топ игроков", callback_data="top_players")],
    [InlineKeyboardButton(text="💬 Посмотреть топ чатов", callback_data="top_chats")]
])
submit_idea_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💡 Предложить идею", url="https://t.me/Project_X")]
])
