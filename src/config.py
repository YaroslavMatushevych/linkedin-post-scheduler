import os


GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_PERSON_URN = os.environ["LINKEDIN_PERSON_URN"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]

# How many top HN stories to consider
HN_CANDIDATE_POOL = 60
HN_MIN_SCORE = 150

# Breaking news configuration
BREAKING_NEWS_MIN_SCORE = 100  # Lower threshold for breaking news (shows up faster)
BREAKING_NEWS_CHECK_INTERVAL = 3600  # Check every hour (3600 seconds)

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

# Breaking news keywords - broader scope for news that affects tech industry
BREAKING_NEWS_KEYWORDS = [
    # Security & Privacy
    "security", "breach", "vulnerability", "exploit", "ransomware", "malware",
    "hacking", "zero-day", "cyber", "privacy", "data leak",
    
    # AI & LLMs
    "ai", "artificial intelligence", "llm", "language model", "gpt", "claude",
    "generative", "machine learning", "chatgpt", "gemini",
    
    # Major Tech Companies & Products
    "apple", "google", "microsoft", "amazon", "meta", "openai", "anthropic",
    "nvidia", "tesla", "intel", "twitter", "stripe", "figma",
    
    # Critical Infrastructure & Policy
    "internet", "outage", "dns", "bgp", "infrastructure", "regulation",
    "antitrust", "dou", "fcc", "congress", "eu laws",
    
    # Emerging Tech
    "quantum", "blockchain", "crypto", "web3", "ar/vr", "metaverse",
    
    # Developer Tools & Languages
    "rust", "go", "python", "typescript", "javascript", "java",
    "kubernetes", "docker", "github", "gitlab", "open source",
    
    # Financial & Economic Impact
    "ipo", "acquisition", "merger", "funding", "layoff", "economic",
    "recession", "inflation", "stock market",
    
    # Industry Trends
    "trend", "innovation", "breakthrough", "launch", "release",
    "framework", "library", "tool", "platform",
]
