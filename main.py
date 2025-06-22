import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from handlers import router
from config import BOT_TOKEN
from database import init_db

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Bot is off')