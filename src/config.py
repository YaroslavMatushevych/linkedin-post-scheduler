import os


GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_PERSON_URN = os.environ["LINKEDIN_PERSON_URN"]
GH_PAT = os.environ["GH_PAT"]  # used for Gist state storage

# How many top HN stories to consider
HN_CANDIDATE_POOL = 60
HN_MIN_SCORE = 150

# Topics relevant to a senior software engineer
RELEVANT_KEYWORDS = [
    "engineering", "software", "developer", "programming", "architecture",
    "performance", "scalability", "distributed", "microservices", "api",
    "typescript", "python", "rust", "golang", "llm", "ai", "ml",
    "devops", "kubernetes", "postgres", "database", "open source",
    "career", "leadership", "team", "startup", "productivity",
    "debugging", "testing", "ci/cd", "security", "observability",
    "react", "backend", "frontend", "system design", "refactoring",
]
