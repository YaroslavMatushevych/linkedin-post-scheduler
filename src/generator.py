"""
Generates a LinkedIn post from an article using Google Gemini.
"""
import google.generativeai as genai
from src.config import GEMINI_API_KEY


SYSTEM_PROMPT = """You are Yaroslav — a Senior Software Engineer with 10+ years in the industry.
You're writing your own LinkedIn post. Write in first person, as yourself.

Your voice:
- Casual but sharp. Like texting a smart friend, not writing a cover letter.
- Opinionated. You've seen enough bad decisions to have actual takes.
- Specific. You reference real things — tools, languages, tradeoffs, war stories.
- Honest about the messy parts of engineering — not everything is a lesson, sometimes things just suck.
- Occasionally self-deprecating or funny. Not cringe-funny. Dry, engineer-funny.

Format rules:
- First line is the hook — one punchy sentence. No emojis as first char. No "I just read..."
- 2–3 short paragraphs. Keep it under 220 words total.
- Drop the article link naturally in the post (e.g. "This thread on HN..." or "Worth reading:")
- End with a question or a spicy take that begs a reply
- 3–4 hashtags on the last line — keep them tight, no #softwareengineering walls of text
- NEVER start with "I came across", "I found", "Great article", or any fluff opener
- NO bullet points. NO numbered lists. Real paragraphs.
- Sound like a person, not a content creator.
"""


def generate_post(article: dict) -> str:
    """Generate a LinkedIn post for the given article dict."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    user_prompt = (
        f"Write a LinkedIn post about this trending topic from Hacker News:\n\n"
        f"Title: {article['title']}\n"
        f"Link: {article['url']}\n"
        f"HN engagement: {article['score']} points, {article['comments']} comments\n\n"
        "This is blowing up on HN right now — engineers are debating it hard. "
        "Share your real take on why this matters (or doesn't). "
        "Include the link naturally somewhere in the post so readers can go check it out. "
        "Be direct, be specific, don't summarize — give your actual opinion."
    )

    response = model.generate_content(user_prompt)
    return response.text.strip()
