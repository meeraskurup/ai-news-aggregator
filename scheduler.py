"""Daily scheduler for fetching and processing news articles."""

import sys
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.models import SessionLocal, Article, init_db
from app.services.fetcher import fetch_all_feeds
from app.services.parser import extract_article_content
from app.services.summarizer import summarize_article
from app.services.categorizer import categorize_article


def cleanup_old_articles(days: int = 7):
    """
    Delete articles older than the specified number of days.
    
    Args:
        days: Number of days to keep articles (default: 7)
    
    Returns:
        Number of articles deleted
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = db.query(Article).filter(Article.fetched_at < cutoff_date).delete()
        db.commit()
        print(f"Cleaned up {deleted_count} articles older than {days} days")
        return deleted_count
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def process_articles():
    """Fetch, process, and store new articles from all sources."""
    print(f"\n{'='*60}")
    print(f"Starting news fetch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Initialize database
    init_db()
    
    # Clean up old articles before fetching new ones
    print("Cleaning up old articles...")
    cleanup_old_articles(days=7)
    
    # Fetch all articles from RSS feeds
    print("Fetching articles from RSS feeds...")
    raw_articles = fetch_all_feeds()
    print(f"Found {len(raw_articles)} AI-relevant articles")
    
    # Create database session
    db = SessionLocal()
    
    new_count = 0
    error_count = 0
    
    try:
        for i, article_data in enumerate(raw_articles, 1):
            url = article_data["url"]
            
            # Check if article already exists
            existing = db.query(Article).filter(Article.url == url).first()
            if existing:
                continue
            
            print(f"\n[{i}/{len(raw_articles)}] Processing: {article_data['title'][:60]}...")
            
            try:
                # Extract full content
                print("  - Extracting content...")
                content = extract_article_content(url)
                
                if not content:
                    print("  - Warning: Could not extract content, using description")
                    content = article_data.get("description", "")
                
                # Generate summary
                print("  - Generating summary...")
                summary = summarize_article(content, article_data["title"])
                
                # Categorize article
                print("  - Categorizing...")
                category = categorize_article(
                    article_data["title"],
                    content,
                    article_data.get("category_hint", "")
                )
                
                # Create new article record
                new_article = Article(
                    title=article_data["title"],
                    url=url,
                    source_name=article_data["source_name"],
                    source_url=article_data["source_url"],
                    category=category,
                    summary=summary,
                    full_content=content[:10000] if content else None,  # Limit stored content
                    published_at=article_data.get("published_at"),
                    fetched_at=datetime.utcnow()
                )
                
                db.add(new_article)
                db.commit()
                
                new_count += 1
                print(f"  - Saved! Category: {category}")
                
            except Exception as e:
                print(f"  - Error processing article: {e}")
                error_count += 1
                db.rollback()
                continue
    
    finally:
        db.close()
    
    print(f"\n{'='*60}")
    print(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"New articles: {new_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*60}\n")
    
    return new_count


def run_scheduler():
    """Start the scheduler for daily updates."""
    print("Starting AI News Aggregator Scheduler")
    print(f"Configured to run daily at {settings.DAILY_UPDATE_HOUR:02d}:{settings.DAILY_UPDATE_MINUTE:02d}")
    
    scheduler = BlockingScheduler()
    
    # Schedule daily job
    scheduler.add_job(
        process_articles,
        CronTrigger(
            hour=settings.DAILY_UPDATE_HOUR,
            minute=settings.DAILY_UPDATE_MINUTE
        ),
        id="daily_news_fetch",
        name="Daily AI News Fetch",
        replace_existing=True
    )
    
    print("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped.")


def run_once():
    """Run the article fetch once (for manual updates)."""
    return process_articles()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI News Aggregator Scheduler")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't start scheduler)"
    )
    
    args = parser.parse_args()
    
    if args.once:
        run_once()
    else:
        run_scheduler()
