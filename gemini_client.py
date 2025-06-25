import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import asyncio

genai.configure(api_key="AIzaSyAaxl51LjMOmT3GNvR7a4IxkrzHpauedtg")
model = genai.GenerativeModel("models/gemini-2.0-flash")

executor = ThreadPoolExecutor()

def _generate_summary(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Ошибка при генерации: {e}"


async def summarize_news(news_articles: list[str]) -> str:
    # Ограничим итоговый текст 16000 символами (~4000 токенов)
    max_chars = 16000
    combined_text = ""
    for article in news_articles:
        if len(combined_text) + len(article) > max_chars:
            break
        combined_text += article + "\n\n"

    prompt = (
            "Суммируй и проанализируй следующие новостные статьи. "
            "Выдели главное, избегай повторений. Ответ должен быть развёрнутым, "
            "структурированным и написан на естественном языке. "
            "Используй подзаголовки, абзацы и перечисления, где уместно. "
            "Избегая различных символов которые мешают чтению напрмер # * "
            "Объём текста — максимально возможный, без пропусков важных деталей."
            f"информативным и написан на русском языке:\n\n" + combined_text
    )

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, _generate_summary, prompt)