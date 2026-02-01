"""Article content extraction using newspaper3k."""

from typing import Optional
from newspaper import Article, ArticleException


def extract_article_content(url: str) -> Optional[str]:
    """
    Extract the main content from an article URL.
    
    Args:
        url: The URL of the article to extract
        
    Returns:
        The extracted article text, or None if extraction fails
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        # Return the main text content
        if article.text:
            return article.text
        
        return None
        
    except ArticleException as e:
        print(f"Error extracting article from {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error extracting article from {url}: {e}")
        return None


def extract_article_metadata(url: str) -> dict:
    """
    Extract metadata from an article URL.
    
    Args:
        url: The URL of the article
        
    Returns:
        Dictionary containing article metadata
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        return {
            "title": article.title,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "text": article.text,
            "top_image": article.top_image,
            "keywords": article.keywords if hasattr(article, 'keywords') else []
        }
        
    except Exception as e:
        print(f"Error extracting metadata from {url}: {e}")
        return {}
