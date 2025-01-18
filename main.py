from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from content_finder import ContentFinder

load_dotenv()

app = FastAPI(
    title="Content Finder API",
    description="API for finding and analyzing content based on media insights",
    version="1.0.0"
)

class MediaInsights(BaseModel):
    primaryAudienceDemographics: str
    painPointsAddressed: List[str]
    competitors: List[str]
    marketPosition: str

API_KEY = os.getenv("API_KEY", "hidev")
content_finder = ContentFinder()

def verify_api_key(api_key: str):
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/")
async def root():
    return {"message": "Welcome to Content Finder API"}

@app.post("/analyze-content")
async def analyze_content(insights: MediaInsights, api_key: str = None):
    verify_api_key(api_key)
    
    # Extract industry terms
    industry_terms = content_finder.extract_industry_terms(insights.dict())
    
    # Get news content
    news_content = content_finder.get_news_content(
        industry_terms.get('industries', []),
        industry_terms.get('products', [])
    )
    
    # Get social media content
    social_content = content_finder.get_social_media_content(
        industry_terms.get('industries', []),
        industry_terms.get('products', [])
    )
    
    # Get competitor content
    competitor_content = content_finder.get_competitor_content(insights.competitors)
    
    return {
        "status": "success",
        "data": {
            "industry_terms": industry_terms,
            "news_content": news_content,
            "social_content": social_content,
            "competitor_content": competitor_content
        }
    }

@app.post("/news-content")
async def get_news(insights: MediaInsights, api_key: str = None):
    verify_api_key(api_key)
    industry_terms = content_finder.extract_industry_terms(insights.dict())
    news_content = content_finder.get_news_content(
        industry_terms.get('industries', []),
        industry_terms.get('products', [])
    )
    return {"status": "success", "data": news_content}

@app.post("/social-content")
async def get_social(insights: MediaInsights, api_key: str = None):
    verify_api_key(api_key)
    industry_terms = content_finder.extract_industry_terms(insights.dict())
    social_content = content_finder.get_social_media_content(
        industry_terms.get('industries', []),
        industry_terms.get('products', [])
    )
    return {"status": "success", "data": social_content}

@app.post("/competitor-content")
async def get_competitor(insights: MediaInsights, api_key: str = None):
    verify_api_key(api_key)
    competitor_content = content_finder.get_competitor_content(insights.competitors)
    return {"status": "success", "data": competitor_content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
