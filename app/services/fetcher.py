"""RSS feed fetcher for news sources."""

import feedparser
from datetime import datetime
from typing import List, Dict, Optional
from time import mktime
import re

from app.config import settings


def is_ai_relevant(title: str, description: str = "") -> bool:
    """Check if an article is relevant to AI based on keywords."""
    text = f"{title} {description}".lower()
    return any(keyword in text for keyword in settings.AI_KEYWORDS)


def parse_date(entry) -> Optional[datetime]:
    """Parse publication date from feed entry."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.fromtimestamp(mktime(entry.published_parsed))
    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime.fromtimestamp(mktime(entry.updated_parsed))
    return None


def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def fetch_feed(source: Dict) -> List[Dict]:
    """
    Fetch articles from a single RSS feed.
    
    Args:
        source: Dictionary containing feed info (name, feed_url, category_hint)
        
    Returns:
        List of article dictionaries
    """
    articles = []
    
    try:
        feed = feedparser.parse(source["feed_url"])
        
        for entry in feed.entries:
            title = entry.get("title", "")
            description = clean_html(entry.get("description", "") or entry.get("summary", ""))
            
            # Filter for AI-relevant content
            if not is_ai_relevant(title, description):
                continue
            
            article = {
                "title": title,
                "url": entry.get("link", ""),
                "source_name": source["name"],
                "source_url": source["feed_url"],
                "description": description[:500] if description else "",
                "published_at": parse_date(entry),
                "category_hint": source.get("category_hint", "")
            }
            
            if article["url"]:  # Only add if we have a URL
                articles.append(article)
                
    except Exception as e:
        print(f"Error fetching feed {source['name']}: {e}")
    
    return articles


def fetch_all_feeds() -> List[Dict]:
    """
    Fetch articles from all configured news sources.
    
    Returns:
        List of all article dictionaries, deduplicated by URL
    """
    all_articles = []
    seen_urls = set()
    
    for source in settings.NEWS_SOURCES:
        articles = fetch_feed(source)
        
        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                all_articles.append(article)
    
    # Sort by publication date (newest first)
    all_articles.sort(
        key=lambda x: x.get("published_at") or datetime.min,
        reverse=True
    )
    
    return all_articles
