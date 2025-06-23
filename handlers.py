from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import keyboards as kb
from database import create_or_update_user, get_user_profile, insert_default_newslinks_once, get_all_links_by_column

router = Router()

class user(StatesGroup):
    telegram_id = State()
    language = State()

class news_structure(StatesGroup):
    category = State()
    bias = State()

@router.message(CommandStart())
async def handler_start(message: Message):
    await message.answer('👋 Welcome to the German News aggregator bot!\n Type /help to find out what this bot can do.')

@router.message(Command("help"))
async def handler_help(message: Message):
    await message.answer(
        "ℹ️ <b>Help Menu</b>\n\n"
        "🧾 <b>/start</b> — Start interacting with the bot\n"
        "⚙️ <b>/registration</b> — Register or update your settings\n"
        "👤 <b>/profile</b> — View your current profile\n"
        "📰 <b>/news</b> — Latest news\n"
        "❓ <b>/help</b> — Show this help menu",
        parse_mode="HTML"
    )

@router.message(Command("profile"))
async def handler_profile(message: Message):
    telegram_id = message.from_user.id
    profile = await get_user_profile(telegram_id)

    if "error" in profile:
        await message.answer(profile["error"])
    else:
        await message.answer(
            f"📋 Your Profile:\n"
            f"🗣 Language: {profile['language']}"
        )

@router.message(Command("registration"))
async def handler_select_of_id(message: Message,  state: FSMContext):
    user_id = message.from_user.id

    await state.update_data(telegram_id=user_id)

    await message.answer('Select the language in which you want to receive news', reply_markup=kb.language_keyboard)
    await state.set_state(user.language)

@router.callback_query(user.language, lambda c: c.data in ['ru', 'de', 'en'])
async def handler_select_language_callback(callback: CallbackQuery, state: FSMContext):
    language = callback.data
    await state.update_data(language=language)

    data = await state.get_data()
    telegram_id = data.get('telegram_id')
    language = data.get('language')

    await create_or_update_user(
        telegram_id=telegram_id,
        language=language
    )

    await callback.message.answer("Great!")
    await state.clear()
    await callback.answer()


@router.message(Command('news'))
async def handler_news(message: Message, state: FSMContext):
    await insert_default_newslinks_once()

    await message.answer('Select the news category you want to receive!', reply_markup=kb.category_button)
    await state.set_state(news_structure.category)

@router.message(news_structure.category, F.text.in_(['politics', 'economics', 'technology', 'general news']))
async def handler_news_select_category(message: Message, state: FSMContext):
    category = message.text
    await state.update_data(category=category)

    await message.answer('Select the news bias category you want to receive!', reply_markup=kb.bias_button)
    await state.set_state(news_structure.bias)

@router.message(news_structure.bias, F.text.in_(['Left', 'Right', 'Center']))
async def handler_news_output(message: Message, state: FSMContext):
    bias = message.text
    await state.update_data(bias=bias)

    data = await state.get_data()
    category = data.get('category')

    links = await get_all_links_by_column(category, bias)






