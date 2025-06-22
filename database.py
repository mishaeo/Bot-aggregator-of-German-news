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
            
            technologiesLeft TEXT,
            technologiesRight TEXT,
            technologiesCenter TEXT,
            
            policyLeft TEXT,
            policyRight TEXT,
            policyCenter TEXT,
            
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