# from fastapi import APIRouter, HTTPException, Body
# from app.models import CropInput, RecommendResponse, CropRecommendation
# # from backend.app.ml.crop_predictor_v2 import get_predictor
# from app.ml.crop_predictor_v2 import get_predictor
# from app.services.weather import get_weather_by_coords

# router = APIRouter()

# @router.post("/recommend", response_model=RecommendResponse)
# async def recommend(input: CropInput = Body(...)):
#     """
#     Main recommendation endpoint.
#     - Validates inputs
#     - (Optionally) enriches temperature using OpenWeather
#     - Uses ML model with confidence + ranges
#     - Returns ranked crop recommendations
#     """
#     print(f"Received input: {input}")

#     # 1) Basic validations
#     if not input.soil_type:
#         raise HTTPException(status_code=400, detail="Soil type is required")

#     if input.pH < 0 or input.pH > 14:
#         raise HTTPException(status_code=400, detail="Invalid pH value")

#     if input.rainfall_30 < 0:
#         raise HTTPException(status_code=400, detail="Rainfall cannot be negative")

#     # 2) Crop mapping logic
#     crop_map = {
#         "Loamy": ["Maize", "Soybean", "Potato"],
#         "Alluvial": ["Rice", "Wheat", "Sugarcane"],
#         "Sandy": ["Millet", "Groundnut", "Sesame"],
#         "Clayey": ["Rice", "Cotton", "Mustard"],
#     }

#     candidates = crop_map.get(input.soil_type, ["Maize", "Wheat", "Rice"])
#     results = []

#     # 3) Optional weather enrichment (lat used for both lat/lon placeholder)
#     weather = get_weather_by_coords(input.lat, input.lon)
#     if weather:
#         main = weather.get("main", {})
#         temp = main.get("temp")
#         if temp is not None:
#             print(f"Overriding avg_temp_30 with OpenWeather temp: {temp}")
#             input.avg_temp_30 = float(temp)

#     predictor = get_predictor()

#     # 4) Prediction loop with confidence & ranges
#     try:
#         for crop in candidates:
#             metrics = predictor.predict_with_confidence(
#                 soil_type=input.soil_type,
#                 ph=input.pH,
#                 rainfall_30=input.rainfall_30,
#                 avg_temp_30=input.avg_temp_30,
#                 lat=input.lat,
#                 irrigation=input.irrigation,
#             )

#             est_yield = metrics["prediction"]
#             est_profit = est_yield * 10  # placeholder INR/acre
#             confidence = metrics["confidence"]
#             min_yield = metrics["min_yield"]
#             max_yield = metrics["max_yield"]

#             results.append(
#                 CropRecommendation(
#                     crop=crop,
#                     estimated_yield_kg_per_acre=est_yield,
#                     estimated_profit_inr_per_acre=est_profit,
#                     risk="low",  # you can later derive this from confidence / range
#                     confidence=confidence,
#                     min_yield=min_yield,
#                     max_yield=max_yield,
#                 )
#             )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Prediction failed: {str(e)}",
#         )

#     return RecommendResponse(recommendations=results)


# @router.get("/model-info")
# def get_model_info():
#     """
#     Get ML model information including metrics and feature importance
#     """
#     try:
#         predictor = get_predictor()
#         return predictor.get_model_info()
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to get model info: {str(e)}",
#         )

from fastapi import APIRouter, HTTPException, Body

from app.models import (
    CropInput,
    RecommendResponse,
    CropRecommendation,
)

from app.ml.crop_predictor_v2 import get_predictor

router = APIRouter()


@router.post(
    "/recommend",
    response_model=RecommendResponse,
)
async def recommend(
    input: CropInput = Body(...)
):

    predictor = get_predictor()

    try:

        results = []

        for crop in predictor.get_candidate_crops(
            season=input.season,
            state=input.state,
        ):

            metrics = predictor.predict_crop_yield(
                crop=crop,
                crop_year=input.crop_year,
                season=input.season,
                state=input.state,
                area=input.area,
                rainfall=input.annual_rainfall,
                fertilizer=input.fertilizer,
                pesticide=input.pesticide,
            )

            results.append(
                {
                    "crop": crop,
                    **metrics,
                }
            )

        results.sort(
            key=lambda x: x["recommendation_score"],
            reverse=True,
        )

        top_3 = results[:3]

        recommendations = []

        for rank, item in enumerate(top_3, start=1):

            recommendations.append(
                CropRecommendation(
                    crop=item["crop"],
                    estimated_yield=item["yield"],
                    estimated_profit=item["estimated_profit"],
                    rank=rank,
                    confidence=item["confidence"],
                    min_yield=item["min_yield"],
                    max_yield=item["max_yield"],
                    yield_index=item["yield_index"],
                    recommendation_score=item["recommendation_score"],
                )
            )

        return RecommendResponse(
            recommendations=recommendations
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/model-info")
def get_model_info():
    try:
        return get_predictor().get_model_info()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
