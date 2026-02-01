"""AI-powered article summarization using OpenAI API."""

import re
from typing import Optional, List
from openai import OpenAI

from app.config import settings


def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client if API key is configured."""
    if settings.OPENAI_API_KEY:
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    return None


def summarize_article(content: str, title: str = "") -> Optional[str]:
    """
    Generate a 6-sentence synthesized summary of an article using OpenAI.
    
    Args:
        content: The full article text
        title: The article title (optional, for context)
        
    Returns:
        A 6-sentence synthesized summary, or fallback if API unavailable
    """
    client = get_openai_client()
    
    if not client:
        # Fallback: use extractive summarization with important sentence selection
        return fallback_summarize(content, title)
    
    try:
        # Truncate content if too long (to manage API costs)
        max_chars = 8000
        truncated_content = content[:max_chars] if len(content) > max_chars else content
        
        prompt = f"""Synthesize and summarize this AI news article in exactly 6 sentences.

IMPORTANT: DO NOT copy sentences directly from the article. Instead, write an original summary in your own words that:
1. States the main news, announcement, or development
2. Identifies the key players (companies, researchers, products)
3. Explains the technical significance or innovation
4. Describes the potential impact or implications
5. Provides relevant context (market, competition, timeline)
6. Concludes with future outlook or next steps

Write as a professional tech journalist synthesizing the information, not quoting it.

Title: {title}

Article Content:
{truncated_content}

Your 6-sentence synthesized summary:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert tech journalist who synthesizes AI news into clear, original summaries. You never copy text directly from articles - you always rewrite information in your own words while maintaining accuracy."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.4
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return fallback_summarize(content, title)


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using regex.
    
    Args:
        text: The text to split
        
    Returns:
        List of sentences
    """
    # Clean up the text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split on sentence boundaries (period, exclamation, question mark followed by space and capital)
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(sentence_pattern, text)
    
    # Filter out very short sentences (likely artifacts)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    
    return sentences


def score_sentence(sentence: str, title: str, position: int, total: int) -> float:
    """
    Score a sentence for importance based on various factors.
    
    Args:
        sentence: The sentence to score
        title: The article title (for keyword matching)
        position: Position of sentence in article
        total: Total number of sentences
        
    Returns:
        Importance score (higher = more important)
    """
    score = 0.0
    sentence_lower = sentence.lower()
    title_lower = title.lower()
    
    # Title word overlap (words from title appearing in sentence)
    title_words = set(re.findall(r'\b\w{4,}\b', title_lower))
    sentence_words = set(re.findall(r'\b\w{4,}\b', sentence_lower))
    overlap = len(title_words & sentence_words)
    score += overlap * 2
    
    # AI/tech keywords boost
    important_keywords = [
        'announced', 'launched', 'released', 'developed', 'introduced',
        'ai', 'artificial intelligence', 'machine learning', 'model',
        'breakthrough', 'innovation', 'research', 'study', 'found',
        'million', 'billion', 'percent', 'growth', 'market',
        'ceo', 'company', 'startup', 'partnership', 'acquisition'
    ]
    for keyword in important_keywords:
        if keyword in sentence_lower:
            score += 1.5
    
    # Position scoring (first and last paragraphs often contain key info)
    if position < total * 0.2:  # First 20%
        score += 3
    elif position > total * 0.8:  # Last 20%
        score += 1.5
    
    # Sentence length (prefer medium-length sentences)
    word_count = len(sentence.split())
    if 15 <= word_count <= 35:
        score += 1
    
    # Contains numbers (often important facts)
    if re.search(r'\d+', sentence):
        score += 1
    
    # Contains quotes (expert opinions)
    if '"' in sentence or '"' in sentence:
        score += 0.5
    
    return score


def fallback_summarize(content: str, title: str = "", num_sentences: int = 6) -> str:
    """
    Extractive summarization fallback when API is unavailable.
    Selects the most important sentences from the article.
    
    Args:
        content: The article text
        title: The article title for context
        num_sentences: Number of sentences to extract
        
    Returns:
        Summary composed of important sentences
    """
    sentences = split_into_sentences(content)
    
    if not sentences:
        # Last resort: just take first chunk of content
        return content[:600] + "..." if len(content) > 600 else content
    
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
    
    # Score each sentence
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = score_sentence(sentence, title, i, len(sentences))
        scored_sentences.append((i, sentence, score))
    
    # Sort by score (highest first)
    scored_sentences.sort(key=lambda x: x[2], reverse=True)
    
    # Take top N sentences
    top_sentences = scored_sentences[:num_sentences]
    
    # Sort by original position to maintain narrative flow
    top_sentences.sort(key=lambda x: x[0])
    
    # Join sentences
    summary = " ".join(s[1] for s in top_sentences)
    
    return summary
