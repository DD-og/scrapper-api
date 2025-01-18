from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Media Insights API",
    description="API for retrieving media insights and analytics",
    version="1.0.0"
)

class MediaInsights(BaseModel):
    primaryAudienceDemographics: str
    painPointsAddressed: List[str]
    competitors: List[str]
    marketPosition: str

API_KEY = os.getenv("API_KEY")

def verify_api_key(api_key: str):
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/")
async def root():
    return {"message": "Welcome to Media Insights API"}

@app.post("/analyze")
async def analyze_media(insights: MediaInsights, api_key: str = None):
    verify_api_key(api_key)
    return {
        "status": "success",
        "data": insights.dict(),
        "analysis": {
            "audience_reach": "High",
            "market_competition": len(insights.competitors),
            "pain_points_identified": len(insights.painPointsAddressed)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
