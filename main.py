from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from content_finder import ContentFinder
import logging
import traceback
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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
    try:
        verify_api_key(api_key)
        logger.info("Starting content analysis")
        
        # Extract industry terms
        industry_terms = content_finder.extract_industry_terms(insights.dict())
        logger.info(f"Extracted industry terms: {industry_terms}")
        
        # Get news content
        news_content = content_finder.search_news_api(
            f"{' '.join(industry_terms.get('industries', []))} {' '.join(industry_terms.get('product_terms', []))}"
        )
        logger.info("Retrieved news content")
        
        # Get social media content
        social_content = content_finder.search_reddit(
            f"{' '.join(industry_terms.get('industries', []))} {' '.join(industry_terms.get('product_terms', []))}"
        )
        logger.info("Retrieved social media content")
        
        # Get competitor content
        competitor_content = []
        for competitor in insights.competitors:
            try:
                content = content_finder.search_medium(competitor)
                competitor_content.extend(content)
            except Exception as e:
                logger.error(f"Error getting competitor content for {competitor}: {str(e)}")
        logger.info("Retrieved competitor content")
        
        return {
            "status": "success",
            "data": {
                "industry_terms": industry_terms,
                "news_content": news_content,
                "social_content": social_content,
                "competitor_content": competitor_content
            }
        }
    except Exception as e:
        logger.error(f"Error in analyze_content: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/news-content")
async def get_news(insights: MediaInsights, api_key: str = None):
    try:
        verify_api_key(api_key)
        logger.info("Starting news content search")
        industry_terms = content_finder.extract_industry_terms(insights.dict())
        news_content = content_finder.search_news_api(
            f"{' '.join(industry_terms.get('industries', []))} {' '.join(industry_terms.get('product_terms', []))}"
        )
        logger.info("Retrieved news content")
        return {"status": "success", "data": news_content}
    except Exception as e:
        logger.error(f"Error in get_news: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/social-content")
async def get_social(insights: MediaInsights, api_key: str = None):
    try:
        verify_api_key(api_key)
        logger.info("Starting social content search")
        industry_terms = content_finder.extract_industry_terms(insights.dict())
        social_content = content_finder.search_reddit(
            f"{' '.join(industry_terms.get('industries', []))} {' '.join(industry_terms.get('product_terms', []))}"
        )
        logger.info("Retrieved social content")
        return {"status": "success", "data": social_content}
    except Exception as e:
        logger.error(f"Error in get_social: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/competitor-content")
async def get_competitor(insights: MediaInsights, api_key: str = None):
    try:
        verify_api_key(api_key)
        logger.info("Starting competitor content search")
        competitor_content = []
        for competitor in insights.competitors:
            try:
                content = content_finder.search_medium(competitor)
                competitor_content.extend(content)
            except Exception as e:
                logger.error(f"Error getting competitor content for {competitor}: {str(e)}")
        logger.info("Retrieved competitor content")
        return {"status": "success", "data": competitor_content}
    except Exception as e:
        logger.error(f"Error in get_competitor: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
