import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import asyncio
from config import AI_TOKEN

genai.configure(api_key=AI_TOKEN)
model = genai.GenerativeModel("models/gemini-2.0-flash")

executor = ThreadPoolExecutor()

def _generate_summary(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Ошибка при генерации: {e}"


async def summarize_news(news_articles: list[str], output_language: str) -> str:
    max_chars = 16000
    combined_text = ""
    for article in news_articles:
        if len(combined_text) + len(article) > max_chars:
            break
        combined_text += article + "\n\n"

    prompt = (
        f"Проанализируй и суммируй следующие новостные статьи. "
        f"Ответ должен быть написан на {output_language} языке.\n\n"
        "🔹 Выдели ключевые события, факты и тенденции.\n"
        "🔹 Избегай повторов между статьями.\n"
        "🔹 Используй подзаголовки, списки и абзацы для структурирования.\n"
        "🔹 Пиши понятно, без символов вроде # * >.\n"
        "🔹 Старайся охватить всё важное, избегая избыточности.\n\n"
        "Вот статьи:\n\n"
        f"{combined_text}"
    )

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, _generate_summary, prompt)
