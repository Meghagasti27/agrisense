# from pydantic import BaseModel
# from typing import List, Optional


# class CropInput(BaseModel):
#     soil_type: str
#     pH: float
#     rainfall_30: float
#     avg_temp_30: float
#     lat: float
#     lon: float
#     irrigation: bool = False


# class CropRecommendation(BaseModel):
#     crop: str
#     estimated_yield_kg_per_acre: float
#     estimated_profit_inr_per_acre: float
#     risk: str
#     confidence: Optional[float] = None
#     min_yield: Optional[float] = None
#     max_yield: Optional[float] = None


# class RecommendResponse(BaseModel):
#     recommendations: List[CropRecommendation]

from pydantic import BaseModel
from typing import List


class CropInput(BaseModel):
    crop_year: int
    season: str
    state: str
    area: float
    annual_rainfall: float
    fertilizer: float
    pesticide: float


class CropRecommendation(BaseModel):
    crop: str
    estimated_yield: float
    estimated_profit: float
    rank: int
    confidence: float
    min_yield: float
    max_yield: float
    yield_index: float
    recommendation_score: float


class RecommendResponse(BaseModel):
    recommendations: List[CropRecommendation]
