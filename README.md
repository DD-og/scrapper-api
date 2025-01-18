# Content Finder

This Python script helps you find related YouTube videos, blog posts, and other web content based on a given text query.

## Features

- Search for relevant YouTube videos
- Find related blog posts and web content
- Configurable number of results
- Easy-to-use API

## Prerequisites

- Python 3.6 or higher
- YouTube Data API key
- Google Custom Search API key
- Google Custom Search Engine ID

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example` and add your API keys:
```bash
cp .env.example .env
```

3. Edit the `.env` file and add your API keys:
- Get a YouTube Data API key from [Google Cloud Console](https://console.cloud.google.com/)
- Get a Google Custom Search API key from [Google Cloud Console](https://console.cloud.google.com/)
- Create a Custom Search Engine and get the Search Engine ID from [Google Programmable Search Engine](https://programmablesearchengine.google.com/)

## Usage

```python
from content_finder import ContentFinder

# Initialize the ContentFinder
finder = ContentFinder()

# Search for content
query = "your search query here"
youtube_results = finder.search_youtube(query, max_results=5)
web_results = finder.search_web_content(query, max_results=5)

# Process results
for video in youtube_results:
    print(f"YouTube Video: {video['title']} - {video['url']}")

for content in web_results:
    print(f"Web Content: {content['title']} - {content['link']}")
```

## API Reference

### ContentFinder Class

#### search_youtube(query, max_results=5)
Searches for YouTube videos related to the query.
- Returns a list of dictionaries containing video information (title, description, URL, thumbnail)

#### search_web_content(query, max_results=5)
Searches for web content related to the query.
- Returns a list of dictionaries containing content information (title, link, snippet)
