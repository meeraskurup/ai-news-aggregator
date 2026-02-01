"""Article categorization into AI subcategories."""

from typing import Optional
from openai import OpenAI

from app.config import settings


# Category keywords for fallback classification
CATEGORY_KEYWORDS = {
    "Large Language Models (LLMs)": [
        "chatgpt", "gpt-4", "gpt-5", "claude", "gemini", "llama", "mistral",
        "llm", "large language model", "language model", "chat bot", "chatbot",
        "openai", "anthropic", "text generation", "prompt", "conversation ai"
    ],
    "Computer Vision & Image Generation": [
        "dall-e", "midjourney", "stable diffusion", "image generation",
        "computer vision", "image recognition", "video generation", "sora",
        "visual ai", "image ai", "diffusion model", "text-to-image",
        "object detection", "face recognition", "image synthesis"
    ],
    "AI Research & Breakthroughs": [
        "research", "paper", "study", "breakthrough", "discovery",
        "benchmark", "dataset", "training", "model architecture",
        "neural network", "deep learning", "algorithm", "innovation",
        "academic", "researcher", "scientist", "laboratory"
    ],
    "AI in Industry": [
        "healthcare", "medical", "finance", "banking", "automotive",
        "manufacturing", "retail", "enterprise", "business application",
        "robotics", "automation", "supply chain", "logistics",
        "industry", "sector", "deployment", "implementation"
    ],
    "AI Ethics & Regulation": [
        "ethics", "regulation", "policy", "law", "governance",
        "bias", "fairness", "safety", "risk", "privacy",
        "responsible ai", "ai act", "legislation", "compliance",
        "transparency", "accountability", "eu ai", "congress"
    ],
    "AI Startups & Business": [
        "startup", "funding", "investment", "acquisition", "merger",
        "valuation", "series", "venture", "ipo", "launch",
        "company", "ceo", "founder", "billion", "million",
        "market", "revenue", "growth", "business"
    ]
}


def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client if API key is configured."""
    if settings.OPENAI_API_KEY:
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    return None


def categorize_article(title: str, content: str = "", hint: str = "") -> str:
    """
    Categorize an article into one of the AI subcategories.
    
    Args:
        title: The article title
        content: The article content (optional)
        hint: Category hint from the source (optional)
        
    Returns:
        The category name
    """
    client = get_openai_client()
    
    if client:
        return ai_categorize(client, title, content)
    
    return keyword_categorize(title, content, hint)


def ai_categorize(client: OpenAI, title: str, content: str = "") -> str:
    """Use AI to categorize the article."""
    try:
        # Use first 2000 chars of content for context
        context = content[:2000] if content else ""
        
        categories_list = "\n".join(f"- {cat}" for cat in settings.CATEGORIES)
        
        prompt = f"""Categorize the following AI news article into exactly ONE of these categories:

{categories_list}

Article Title: {title}

Article Content Preview:
{context}

Respond with ONLY the category name, nothing else."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at categorizing AI news articles. Respond only with the category name."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=50,
            temperature=0
        )
        
        category = response.choices[0].message.content.strip()
        
        # Validate the category
        if category in settings.CATEGORIES:
            return category
        
        # Try to match partial category name
        for valid_cat in settings.CATEGORIES:
            if valid_cat.lower() in category.lower() or category.lower() in valid_cat.lower():
                return valid_cat
        
        # Fallback to keyword categorization
        return keyword_categorize(title, content, "")
        
    except Exception as e:
        print(f"Error in AI categorization: {e}")
        return keyword_categorize(title, content, "")


def keyword_categorize(title: str, content: str = "", hint: str = "") -> str:
    """
    Fallback keyword-based categorization.
    
    Args:
        title: Article title
        content: Article content
        hint: Category hint from source
        
    Returns:
        Best matching category
    """
    # If we have a valid hint, use it
    if hint in settings.CATEGORIES:
        return hint
    
    text = f"{title} {content}".lower()
    
    # Count keyword matches for each category
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[category] = score
    
    # Return category with highest score, or default
    if scores:
        best_category = max(scores, key=scores.get)
        if scores[best_category] > 0:
            return best_category
    
    # Default category if no matches
    return "AI Research & Breakthroughs"
