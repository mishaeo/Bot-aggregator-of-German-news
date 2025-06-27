from typing import Dict
import aiosqlite


DB_NAME = "database.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS newslinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            bias TEXT NOT NULL,
            url TEXT NOT NULL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            language TEXT DEFAULT 'en'
        )
        """)
        await db.commit()




async def create_or_update_user(telegram_id: int, language: str = 'en'):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (telegram_id, language)
            VALUES (?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                language=excluded.language
        """, (telegram_id, language))
        await db.commit()


async def get_user_profile(telegram_id: int) -> Dict[str, str]:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT language FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()

    if row:
        return {"language": row[0]}
    else:
        return {
            "error": "⚠️ You are not registered yet. Use /registration to register."
        }


async def insert_default_newslinks_once():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM newslinks")
        count = (await cursor.fetchone())[0]

        if count == 0:
            links = [
                # Economics
                ('economics', 'Left', 'https://www.zeit.de/thema/wirtschaftspolitik'),
                ('economics', 'Right', 'https://www.tichyseinblick.de/wirtschaft/'),
                ('economics', 'Center', 'https://www.faz.net/aktuell/wirtschaft'),

                # Technology
                ('technology', 'Left', 'https://www.zeit.de/thema/digitalisierung'),
                ('technology', 'Right', 'https://www.tichyseinblick.de'),
                ('technology', 'Center', 'https://www.faz.net/pro/digitalwirtschaft'),

                # Politics
                ('politics', 'Left', 'https://www.freitag.de/front-page'),
                ('politics', 'Right', 'https://jungefreiheit.de'),
                ('politics', 'Center', 'https://www.tagesspiegel.de/politik'),

                # General News
                ('generalNews', 'Left', 'https://www.sueddeutsche.de'),
                ('generalNews', 'Right', 'https://www.tichyseinblick.de'),
                ('generalNews', 'Center', 'https://www.tagesspiegel.de'),
            ]

            await db.executemany("""
                INSERT INTO newslinks (category, bias, url)
                VALUES (?, ?, ?)
            """, links)
            await db.commit()



async def get_all_links_by_column(category: str, bias: str) -> list[str]:
    valid_categories = ['economics', 'technology', 'politics', 'generalNews']
    valid_biases = ['Left', 'Right', 'Center']

    if category not in valid_categories or bias not in valid_biases:
        raise ValueError("Неверная категория или политический взгляд")

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT url FROM newslinks WHERE category = ? AND bias = ? ORDER BY id",
            (category, bias)
        )
        rows = await cursor.fetchall()

    return [row[0] for row in rows if row[0]]




