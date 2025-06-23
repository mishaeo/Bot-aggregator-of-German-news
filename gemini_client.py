import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY_HERE")

model = genai.GenerativeModel("gemini-pro")


async def summarize_news(news_articles: list[str]) -> str:
    # Объединяем статьи
    combined_text = "\n\n".join(news_articles[:5])  # ограничим объем, чтобы не вылезти за лимит
    prompt = (
            "Суммируй и проанализируй следующие новостные статьи. "
            "Выдели главное, избегай повторений. Ответ должен быть кратким, "
            "информативным и написан на человеческом языке:\n\n" + combined_text
    )

    response = model.generate_content(prompt)
    return response.text
