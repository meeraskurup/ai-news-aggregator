# AI News Aggregator

A Python web application that aggregates AI news from 10 reputable sources, categorizes them into subcategories, and provides AI-generated summaries. Updated daily.

## Features

- **10 Reputable Sources**: MIT Technology Review, The Verge, Wired, Ars Technica, VentureBeat, TechCrunch, The Guardian, Reuters, IEEE Spectrum, and Google AI Blog
- **AI-Powered Summaries**: Each article summarized in 6 sentences using OpenAI GPT
- **Smart Categorization**: Articles sorted into 6 categories:
  - Large Language Models (LLMs)
  - AI Research & Breakthroughs
  - AI in Industry
  - AI Ethics & Regulation
  - AI Startups & Business
- **Daily Updates**: Automatic scheduling fetches new articles every day
- **Modern UI**: Clean, responsive design with TailwindCSS

## Quick Start

### 1. Clone and Setup

```bash
cd ai-news-aggregator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 3. Fetch Initial Articles

```bash
# Run the scheduler once to populate the database
python scheduler.py --once
```

### 4. Start the Web Server

```bash
# Run the FastAPI server
uvicorn app.main:app --reload

# Open http://localhost:8000 in your browser
```

## Usage

### Web Interface

Visit `http://localhost:8000` to browse articles. Use the sidebar to filter by:
- **Category**: Filter by AI topic
- **Source**: Filter by news outlet

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/news/articles` | Get all articles (supports filtering) |
| `GET /api/news/articles?category=LLMs` | Filter by category |
| `GET /api/news/articles?source=TechCrunch` | Filter by source |
| `GET /api/news/today` | Get today's articles |
| `GET /api/news/categories` | Get category list with counts |
| `GET /api/news/sources` | Get source list with counts |
| `GET /api/news/stats` | Get overall statistics |

### Scheduler Options

```bash
# Run once and exit
python scheduler.py --once

# Start continuous scheduler (runs daily at configured time)
python scheduler.py
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# Start both web server and scheduler
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker Only

```bash
# Build the image
docker build -t ai-news-aggregator .

# Run the web server
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  ai-news-aggregator

# Run scheduler separately
docker run -d \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  ai-news-aggregator python scheduler.py
```

## Configuration

Edit `.env` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key for summarization |
| `DATABASE_URL` | `sqlite:///./news.db` | Database connection string |
| `DAILY_UPDATE_HOUR` | `6` | Hour to run daily update (0-23) |
| `DAILY_UPDATE_MINUTE` | `0` | Minute to run daily update (0-59) |
| `DEBUG` | `false` | Enable debug mode |

## Project Structure

```
ai-news-aggregator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Database models
│   ├── services/
│   │   ├── fetcher.py       # RSS feed fetching
│   │   ├── parser.py        # Article content extraction
│   │   ├── summarizer.py    # AI summarization
│   │   └── categorizer.py   # Category classification
│   ├── routes/
│   │   └── news.py          # API endpoints
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── category.html
├── static/
│   └── css/styles.css
├── scheduler.py             # Daily update scheduler
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## News Sources

| Source | Type | Focus |
|--------|------|-------|
| MIT Technology Review | RSS | Research & Innovation |
| The Verge | RSS | Consumer AI, LLMs |
| Wired | RSS | Tech Culture & AI |
| Ars Technica | RSS | Technical Deep Dives |
| VentureBeat | RSS | AI Business & Enterprise |
| TechCrunch | RSS | Startups & Funding |
| The Guardian | RSS | AI Ethics & Society |
| Reuters | RSS | Industry & Business |
| IEEE Spectrum | RSS | Engineering & Research |
| Google AI Blog | RSS | Research & Products |

## Cost Estimation

With OpenAI GPT-3.5-Turbo:
- ~20-50 articles/day average
- ~$0.50-2.00/day for summarization
- ~$15-60/month total

To reduce costs:
- Use the fallback summarizer (extracts first sentences)
- Set `OPENAI_API_KEY` to empty to disable AI features

## License

MIT License - Feel free to use and modify.
