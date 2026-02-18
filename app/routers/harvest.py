from fastapi import APIRouter, HTTPException
from schemas import HarvestRequest, HarvestResponse
from datetime import date
import httpx
import os
import json
import google.generativeai as genai

router = APIRouter()

# Crop Duration Data (in days)
CROP_DURATIONS = {
    "Wheat": 120,
    "Rice": 135,
    "Cotton": 160,
    "Maize": 110,
    "Sugarcane": 365
}

# --- Helper Functions ---

def calculate_maturity(crop_type: str, sowing_date: date):
    """Calculates crop maturity percentage based on sowing date."""
    if crop_type not in CROP_DURATIONS:
        raise HTTPException(status_code=400, detail=f"Unknown crop type: {crop_type}")
    
    today = date.today()
    if sowing_date > today:
        raise HTTPException(status_code=400, detail="Sowing date cannot be in the future")

    days_after_sowing = (today - sowing_date).days
    duration = CROP_DURATIONS[crop_type]
    
    maturity_percent = (days_after_sowing / duration) * 100
    if maturity_percent > 100:
        maturity_percent = 100.0
        
    return days_after_sowing, round(maturity_percent, 2)

async def get_weather_data(location: str):
    """Fetches weather data from OpenWeatherMap."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("Warning: WEATHER_API_KEY not found.")
        return None

    # Using OpenWeatherMap 5 day forecast API (free tier usually available)
    # If location is coord based (e.g. "lat,lon"), handle parsing if needed. 
    # For simplicity assuming city name or "lat,lon" string passed directly to q= or handling logic.
    # The requirement says "city name OR latitude/longitude".
    
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "appid": api_key,
        "units": "metric"
    }

    # Simple heuristic to check if location looks like lat,lon
    if "," in location and any(c.isdigit() for c in location):
        try:
            lat, lon = location.split(",")
            params["lat"] = lat.strip()
            params["lon"] = lon.strip()
        except ValueError:
             params["q"] = location
    else:
        params["q"] = location

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant info
            # 5-day forecast returns list. We can calculate rain prob from "pop" (probability of precipitation)
            forecast_list = data.get("list", [])
            
            # Avg Rain Probability (next 5 days approx 40 datapoints for 3hr intervals, let's take first 24 hrs or avg of all)
            # "pop" is from 0 to 1.
            pop_values = [item.get("pop", 0) for item in forecast_list]
            avg_pop = sum(pop_values) / len(pop_values) if pop_values else 0
            rain_probability = round(avg_pop * 100, 1)

            # Max Wind Speed
            wind_speeds = [item.get("wind", {}).get("speed", 0) for item in forecast_list]
            max_wind_speed = max(wind_speeds) if wind_speeds else 0

            # Storm Check (This is simplified. Weather codes 2xx are thunderstorms)
            storm_alert = any(
                str(weather.get("id", "")).startswith("2") 
                for item in forecast_list 
                for weather in item.get("weather", [])
            )

            weather_summary = f"Rain Prob: {rain_probability}%, Max Wind: {max_wind_speed}km/h"
            if storm_alert:
                weather_summary += ", Storm Alert!"

            return {
                "rain_probability": rain_probability,
                "wind_speed": max_wind_speed,
                "storm_alert": storm_alert,
                "summary": weather_summary
            }

    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

async def get_gemini_recommendation(data: dict):
    """Sends data to Gemini for reasoning."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        You are an agricultural advisory AI specialized in Indian farming conditions.

        Analyze the farm data below and provide a harvest recommendation.

        FARM DATA:
        Crop Type: {data['crop_type']}
        Days Since Sowing: {data['days_after_sowing']}
        Maturity Percentage: {data['maturity_percent']}%
        Location: {data['location']}
        Rain Probability (Next 5 Days): {data.get('rain_probability', 'N/A')}%
        Wind Speed: {data.get('wind_speed', 'N/A')} km/h
        Storm Alert: {data.get('storm_alert', 'N/A')}

        Decision Rules:
        1. If maturity < 70%, recommend WAIT.
        2. If maturity between 70% and 85%, analyze weather and decide.
        3. If maturity > 85% and rain_probability > 60%, recommend HARVEST NOW.
        4. If storm alert is true and maturity > 80%, recommend HIGH RISK – HARVEST IMMEDIATELY.
        5. Otherwise recommend WAIT.

        Return STRICT JSON in this format:
        {{
            "maturity_status": "",
            "weather_risk_level": "LOW | MEDIUM | HIGH",
            "recommendation": "HARVEST NOW | WAIT | HIGH RISK – HARVEST IMMEDIATELY",
            "reasoning": "",
            "farmer_advice": ""
        }}
        """
        
        # Enforce JSON generation
        response = await model.generate_content_async(prompt)
        
        # Clean response text (remove markdown code blocks if present)
        text = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(text)

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

# --- Main Endpoint ---

@router.post("/api/harvest-predict", response_model=HarvestResponse)
async def predict_harvest(request: HarvestRequest):
    # 1. Calculate Maturity
    days, maturity = calculate_maturity(request.crop_type, request.sowing_date)
    
    # 2. Get Weather
    weather = await get_weather_data(request.location)
    
    # Default weather values if API fails
    if not weather:
        weather = {
            "rain_probability": 0,
            "wind_speed": 0,
            "storm_alert": False,
            "summary": "Weather data unavailable"
        }

    # 3. Get Gemini Recommendation
    gemini_input = {
        "crop_type": request.crop_type,
        "days_after_sowing": days,
        "maturity_percent": maturity,
        "location": request.location,
        **weather
    }
    
    ai_response = await get_gemini_recommendation(gemini_input)

    # Fallback if Gemini fails
    if not ai_response:
        ai_response = {
            "maturity_status": "Calculated based on sowing date",
            "weather_risk_level": "UNKNOWN",
            "recommendation": "WAIT" if maturity < 85 else "HARVEST NOW",
            "reasoning": "AI Service unavailable. Recommendation based on maturity only.",
            "farmer_advice": "Please consult local experts."
        }

    # 4. Construct Final Response
    return HarvestResponse(
        crop_type=request.crop_type,
        days_after_sowing=days,
        maturity_percent=maturity,
        weather_summary=weather["summary"],
        weather_risk_level=ai_response.get("weather_risk_level", "UNKNOWN"),
        recommendation=ai_response.get("recommendation", "WAIT"),
        reasoning=ai_response.get("reasoning", ""),
        farmer_advice=ai_response.get("farmer_advice", "")
    )
