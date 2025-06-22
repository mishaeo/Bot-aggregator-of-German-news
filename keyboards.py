from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

language_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Russian", callback_data="ru"),
        InlineKeyboardButton(text="German", callback_data="de"),
        InlineKeyboardButton(text="English", callback_data="en")
    ]
])