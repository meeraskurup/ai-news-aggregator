"""Configuration settings for the AI News Aggregator."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./news.db")
    
    # Scheduler
    DAILY_UPDATE_HOUR: int = int(os.getenv("DAILY_UPDATE_HOUR", "6"))
    DAILY_UPDATE_MINUTE: int = int(os.getenv("DAILY_UPDATE_MINUTE", "0"))
    
    # App
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # News Sources - 10 Reputable AI News Sources
    NEWS_SOURCES = [
        {
            "name": "MIT Technology Review",
            "feed_url": "https://www.technologyreview.com/feed/",
            "category_hint": "AI Research & Breakthroughs"
        },
        {
            "name": "The Verge AI",
            "feed_url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "category_hint": "Large Language Models (LLMs)"
        },
        {
            "name": "Wired AI",
            "feed_url": "https://www.wired.com/feed/tag/ai/latest/rss",
            "category_hint": "AI Research & Breakthroughs"
        },
        {
            "name": "Ars Technica",
            "feed_url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
            "category_hint": "AI Research & Breakthroughs"
        },
        {
            "name": "VentureBeat AI",
            "feed_url": "https://venturebeat.com/category/ai/feed/",
            "category_hint": "AI Startups & Business"
        },
        {
            "name": "TechCrunch AI",
            "feed_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "category_hint": "AI Startups & Business"
        },
        {
            "name": "The Guardian AI",
            "feed_url": "https://www.theguardian.com/technology/artificialintelligenceai/rss",
            "category_hint": "AI Ethics & Regulation"
        },
        {
            "name": "Reuters Technology",
            "feed_url": "https://www.reuters.com/technology/rss",
            "category_hint": "AI in Industry"
        },
        {
            "name": "IEEE Spectrum AI",
            "feed_url": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
            "category_hint": "AI Research & Breakthroughs"
        },
        {
            "name": "Google AI Blog",
            "feed_url": "https://blog.google/technology/ai/rss/",
            "category_hint": "Large Language Models (LLMs)"
        }
    ]
    
    # AI-related keywords for filtering
    AI_KEYWORDS = [
        "ai", "artificial intelligence", "machine learning", "deep learning",
        "neural network", "gpt", "chatgpt", "llm", "large language model",
        "openai", "anthropic", "claude", "gemini", "transformer",
        "natural language processing", "nlp", "computer vision",
        "generative ai", "gen ai", "dall-e", "midjourney", "stable diffusion",
        "reinforcement learning", "robotics", "automation", "algorithm",
        "data science", "model training", "inference", "embedding",
        "ai safety", "ai ethics", "ai regulation", "agi"
    ]
    
    # Categories
    CATEGORIES = [
        "Large Language Models (LLMs)",
        "AI Research & Breakthroughs",
        "AI in Industry",
        "AI Ethics & Regulation",
        "AI Startups & Business"
    ]

settings = Settings()
