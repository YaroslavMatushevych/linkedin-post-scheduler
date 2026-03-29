"""
Generates a LinkedIn post from an article using Google Gemini.
"""
import google.generativeai as genai
from src.config import GEMINI_API_KEY


SYSTEM_PROMPT = """You are a ghostwriter for Yaroslav, a Senior Software Engineer
with 10+ years of experience. You write his LinkedIn posts.

Style guidelines:
- Hook in the first line (a bold observation, surprising stat, or contrarian take)
- Share a genuine insight or lesson — not just a summary
- Personal, direct voice — like chatting with a smart colleague
- 150–250 words max
- End with an open question to drive comments
- 3–5 relevant hashtags at the bottom (on their own line)
- NO generic filler like "Great article!" or "I found this interesting"
- NO bullet point walls — flowing paragraphs preferred
- Do NOT mention the article title or source directly; weave the insight naturally
"""


def generate_post(article: dict) -> str:
    """Generate a LinkedIn post for the given article dict."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    user_prompt = (
        f"Write a LinkedIn post inspired by this article:\n\n"
        f"Title: {article['title']}\n"
        f"URL: {article['url']}\n"
        f"Source: {article['source']} (score: {article['score']}, "
        f"comments: {article['comments']})\n\n"
        "The post should reflect the perspective of a senior software engineer "
        "who has seen similar challenges first-hand."
    )

    response = model.generate_content(user_prompt)
    return response.text.strip()
