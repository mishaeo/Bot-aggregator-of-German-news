from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

language_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Russian", callback_data="ru"),
        InlineKeyboardButton(text="German", callback_data="de"),
        InlineKeyboardButton(text="English", callback_data="en")
    ]
])

category_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="politics")],
        [KeyboardButton(text="economics")],
        [KeyboardButton(text="technology")],
        [KeyboardButton(text="general news")],
    ],
    resize_keyboard=True
)

bias_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Left")],
        [KeyboardButton(text="Right")],
        [KeyboardButton(text="Center")],
    ],
    resize_keyboard=True
)
