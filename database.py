from typing import Dict
import aiosqlite

DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS newslinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            economicsLeft TEXT,
            economicsRight TEXT,
            economicsCenter TEXT,
            
            technologyLeft TEXT,
            technologyRight TEXT,
            technologyCenter TEXT,
            
            politicsLeft TEXT,
            politicsRight TEXT,
            politicsCenter TEXT,
            
            generalNewsLeft TEXT,
            generalNewsRight TEXT,
            generalNewsCenter TEXT
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
        language = row[0]
        return {
            "language": language
        }
    else:
        return {
            "error": "⚠️ You are not registered yet. Use /registration to register."
        }

async def insert_default_newslinks_once():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM newslinks")
        count = (await cursor.fetchone())[0]

        if count == 0:
            await db.execute("""
                INSERT INTO newslinks (
                    economicsLeft, economicsRight, economicsCenter,
                    technologyLeft, technologyRight, technologyCenter,
                    politicsLeft, politicsRight, politicsCenter,
                    generalNewsLeft, generalNewsRight, generalNewsCenter
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "https://www.zeit.de/thema/wirtschaftspolitik",
                "https://deutsche-wirtschafts-nachrichten.de/wirtschaft/",
                "https://www.handelsblatt.com",

                "https://www.zeit.de/thema/digitalisierung",
                "https://deutsche-wirtschafts-nachrichten.de/technologie/",
                "https://www.faz.net/pro/digitalwirtschaft",

                "https://www.freitag.de/front-page",
                "https://jungefreiheit.de",
                "https://www.cicero.de",

                "https://www.sueddeutsche.de",
                "https://nius.de",
                "https://www.rnd.de"
            ))
            await db.commit()


async def get_all_links_by_column(category: str, bias: str) -> list[str]:
    valid_categories = ['economics', 'technology', 'politics', 'generalNews']
    valid_biases = ['Left', 'Right', 'Center']

    if category not in valid_categories or bias not in valid_biases:
        raise ValueError("Неверная категория или политический взгляд")

    column_name = f"{category}{bias}"  # например: economicsLeft

    async with aiosqlite.connect(DB_NAME) as db:
        query = f"SELECT {column_name} FROM newslinks ORDER BY id"
        cursor = await db.execute(query)
        rows = await cursor.fetchall()

    # Возвращаем только непустые строки
    return [row[0] for row in rows if row[0]]



