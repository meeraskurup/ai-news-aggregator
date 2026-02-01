"""Database models for the AI News Aggregator."""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Article(Base):
    """Model for storing news articles."""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source_name = Column(String(100), nullable=False, index=True)
    source_url = Column(String(500))
    category = Column(String(100), index=True)
    summary = Column(Text)
    full_content = Column(Text)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert article to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "category": self.category,
            "summary": self.summary,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None
        }


class Source(Base):
    """Model for storing news sources."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    feed_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    last_fetched = Column(DateTime)
    
    def to_dict(self):
        """Convert source to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "feed_url": self.feed_url,
            "is_active": self.is_active,
            "last_fetched": self.last_fetched.isoformat() if self.last_fetched else None
        }


def init_db():
    """Initialize the database and create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
