from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from deep_translator import GoogleTranslator
from newspaper import build

import keyboards as kb
from database import create_or_update_user, get_user_profile, insert_default_newslinks_once, get_all_links_by_column
from gemini_client import summarize_news

router = Router()

class user(StatesGroup):
    telegram_id = State()
    language = State()

class news_structure(StatesGroup):
    category = State()
    bias = State()

def build_from_multiple_sites(links):
    all_articles = []
    for url in links:
        try:
            paper = build(url, memoize_articles=False)
            all_articles.extend(paper.articles)
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")
    return all_articles

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

@router.message(news_structure.category, F.text.in_(['politics', 'economics', 'technology', 'generalNews']))
async def handler_news_select_category(message: Message, state: FSMContext):
    category = message.text
    await state.update_data(category=category)

    await message.answer('Select the news bias category you want to receive!', reply_markup=kb.bias_button)
    await state.set_state(news_structure.bias)




@router.message(news_structure.bias, F.text.in_(['Left', 'Right', 'Center']))
async def handler_news_output(message: Message, state: FSMContext):
    await message.answer("Идет сбор и вывод новостей...")

    # Получаем направление
    bias = message.text
    await state.update_data(bias=bias)

    # Получаем предыдущие данные
    data = await state.get_data()
    category = data.get('category')

    # Получаем ссылки на статьи
    links = await get_all_links_by_column(category, bias)

    # Загружаем профиль пользователя и определяем язык
    telegram_id = message.from_user.id
    profile = await get_user_profile(telegram_id)
    user_lang = profile.get('language', 'en')

    # Получаем статьи с сайтов
    all_articles = build_from_multiple_sites(links)

    # Список текстов для перевода
    articles_text = []

    for article in all_articles[:10]:  # ограничим до 10 статей
        try:
            article.download()
            article.parse()
            raw_text = article.text.strip()

            # Получаем первые 2 абзаца
            paragraphs = [p for p in raw_text.split('\n') if p.strip()]
            excerpt = '\n\n'.join(paragraphs[:2])

            if excerpt:
                articles_text.append(excerpt)
        except Exception as e:
            print(f"Ошибка при обработке статьи: {e}")
            continue

    if not articles_text:
        await message.answer("Не удалось получить содержимое ни одной статьи.")
        return

    await message.answer("Поиск новостей завершен") # TEST

    await message.answer("Перевод новостей завершен") # TEST
    await message.answer("Генерирую сводку с помощью ИИ") # TEST

    # Генерация сводки
    summary = await summarize_news(articles_text, user_lang)

    if not summary.strip():
        await message.answer("Не удалось сгенерировать сводку.")
        return

    # Отправка пользователю — учитываем ограничение Telegram
    MAX_LENGTH = 4000
    if len(summary) > MAX_LENGTH:
        summary_parts = [summary[i:i + MAX_LENGTH] for i in range(0, len(summary), MAX_LENGTH)]
        for part in summary_parts:
            await message.answer(part)
    else:
        await message.answer(summary)







