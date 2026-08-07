# DuckDuckGo Search Skill

Advanced web search capability using DuckDuckGo's search engine via Python.

## Overview

This skill provides enhanced web search capabilities using the `duckduckgo-search` Python library. It offers:
- Text search with results
- News search
- Image search
- Answer/Instant answers
- Safe search controls
- Region-specific results

## Installation

```bash
pip install duckduckgo-search
```

## Usage

### Python Module

```python
from skills.duckduckgo_search import DuckDuckGoSearcher

# Initialize
searcher = DuckDuckGoSearcher()

# Text search
results = searcher.text_search("latest AI developments 2026", max_results=10)

# News search
news = searcher.news_search("technology", max_results=5)

# Get instant answer
answer = searcher.get_answer("what is the capital of France")

# Image search
images = searcher.image_search("cyberpunk city", max_results=10)
```

### Command Line

```bash
# Search
python -m skills.duckduckgo_search "latest AI news" --max-results 10

# News
python -m skills.duckduckgo_search --news "technology breakthroughs"

# Images
python -m skills.duckduckgo_search --images "futuristic AI" --max-results 5
```

## Features

- **No API key required** - Free, anonymous searches
- **Fast results** - Direct HTTP requests, no browser automation
- **Multiple search types** - Text, news, images, answers
- **Safe search** - Configurable safety levels
- **Region support** - Search specific regions/languages

## Configuration

```python
searcher = DuckDuckGoSearcher(
    safe_search='moderate',  # 'on', 'moderate', 'off'
    region='us-en',          # Region code
    timeout=30               # Request timeout
)
```

## Integration with Other Skills

Use this skill to enhance research tasks:
- Research topics before creating content
- Find latest news for reports
- Source images for presentations
- Verify facts and find sources
