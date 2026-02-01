"""News API endpoints."""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import get_db, Article
from app.config import settings

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/articles")
def get_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    days: int = Query(7, description="Get articles from the last N days"),
    limit: int = Query(50, description="Maximum number of articles to return"),
    db: Session = Depends(get_db)
):
    """
    Get news articles with optional filtering.
    
    - **category**: Filter by category name
    - **source**: Filter by source name
    - **days**: Get articles from the last N days (default: 7)
    - **limit**: Maximum articles to return (default: 50)
    """
    query = db.query(Article)
    
    # Apply filters
    if category:
        query = query.filter(Article.category == category)
    
    if source:
        query = query.filter(Article.source_name == source)
    
    # Filter by date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(Article.fetched_at >= cutoff_date)
    
    # Order by publication date and limit
    articles = query.order_by(desc(Article.published_at)).limit(limit).all()
    
    return {
        "count": len(articles),
        "articles": [article.to_dict() for article in articles]
    }


@router.get("/articles/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article by ID."""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article.to_dict()


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all categories with article counts."""
    categories = []
    
    for category in settings.CATEGORIES:
        count = db.query(Article).filter(Article.category == category).count()
        categories.append({
            "name": category,
            "count": count
        })
    
    return {"categories": categories}


@router.get("/sources")
def get_sources(db: Session = Depends(get_db)):
    """Get all news sources with article counts."""
    sources = []
    
    for source_config in settings.NEWS_SOURCES:
        count = db.query(Article).filter(
            Article.source_name == source_config["name"]
        ).count()
        sources.append({
            "name": source_config["name"],
            "feed_url": source_config["feed_url"],
            "count": count
        })
    
    return {"sources": sources}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics about the news database."""
    total_articles = db.query(Article).count()
    
    # Get latest article date
    latest = db.query(Article).order_by(desc(Article.fetched_at)).first()
    latest_update = latest.fetched_at.isoformat() if latest else None
    
    # Articles per category
    category_stats = {}
    for category in settings.CATEGORIES:
        category_stats[category] = db.query(Article).filter(
            Article.category == category
        ).count()
    
    # Articles per source
    source_stats = {}
    for source_config in settings.NEWS_SOURCES:
        source_stats[source_config["name"]] = db.query(Article).filter(
            Article.source_name == source_config["name"]
        ).count()
    
    return {
        "total_articles": total_articles,
        "latest_update": latest_update,
        "categories": category_stats,
        "sources": source_stats
    }


@router.get("/today")
def get_today_articles(db: Session = Depends(get_db)):
    """Get all articles from today."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    articles = db.query(Article).filter(
        Article.fetched_at >= today
    ).order_by(desc(Article.published_at)).all()
    
    return {
        "date": today.strftime("%Y-%m-%d"),
        "count": len(articles),
        "articles": [article.to_dict() for article in articles]
    }
