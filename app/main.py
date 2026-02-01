"""Main FastAPI application for AI News Aggregator."""

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
import os

from app.models import init_db, get_db, Article
from app.routes.news import router as news_router
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="AI News Aggregator",
    description="Stay updated with the latest AI innovations from 10 reputable sources",
    version="1.0.0"
)

# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

# Include API routes
app.include_router(news_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    category: str = None,
    source: str = None,
    db: Session = Depends(get_db)
):
    """Render the main news feed page."""
    # Get articles from the last 7 days
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    query = db.query(Article).filter(Article.fetched_at >= cutoff_date)
    
    # Apply filters
    if category:
        query = query.filter(Article.category == category)
    if source:
        query = query.filter(Article.source_name == source)
    
    articles = query.order_by(desc(Article.published_at)).limit(50).all()
    
    # Get category counts for sidebar
    category_counts = {}
    for cat in settings.CATEGORIES:
        category_counts[cat] = db.query(Article).filter(
            Article.category == cat,
            Article.fetched_at >= cutoff_date
        ).count()
    
    # Get source counts
    source_counts = {}
    for src in settings.NEWS_SOURCES:
        source_counts[src["name"]] = db.query(Article).filter(
            Article.source_name == src["name"],
            Article.fetched_at >= cutoff_date
        ).count()
    
    # Get latest update time
    latest = db.query(Article).order_by(desc(Article.fetched_at)).first()
    last_updated = latest.fetched_at if latest else None
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "articles": articles,
            "categories": settings.CATEGORIES,
            "category_counts": category_counts,
            "sources": [s["name"] for s in settings.NEWS_SOURCES],
            "source_counts": source_counts,
            "selected_category": category,
            "selected_source": source,
            "last_updated": last_updated,
            "total_count": len(articles)
        }
    )


@app.get("/category/{category_name}", response_class=HTMLResponse)
async def category_page(
    request: Request,
    category_name: str,
    db: Session = Depends(get_db)
):
    """Render page for a specific category."""
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    articles = db.query(Article).filter(
        Article.category == category_name,
        Article.fetched_at >= cutoff_date
    ).order_by(desc(Article.published_at)).limit(50).all()
    
    return templates.TemplateResponse(
        "category.html",
        {
            "request": request,
            "articles": articles,
            "category_name": category_name,
            "categories": settings.CATEGORIES,
            "total_count": len(articles)
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
