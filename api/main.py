from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json
import re
import base64 # Base64 кодтау/декодтау үшін

app = FastAPI(title="Cyber-Detective API")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.0-flash-lite-preview-02-05" # Әлі де осыны қолданамыз, себебі бұл тұрақты
# Егер 2.5 жұмыс істесе, соны жаз: "gemini-2.5-flash-lite"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

class Message(BaseModel):
    text: str

class ImageAnalysisRequest(BaseModel):
    image_base64: str # Base64 форматтағы сурет деректері

@app.get("/")
def home():
    return {"status": "Cyber-Detective API Online", "model": GEMINI_MODEL}

# --- Мәтінді талдау ---
@app.post("/analyze")
def analyze(msg: Message):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = f"""
    Сен кибер-сарапшысың. Мына мәтінді алаяқтыққа (scam) талда:
    Текст: "{msg.text}"
    
    Жауапты ТЕК қана мына JSON форматында қайтар:
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "confidence": "0-100 арасындағы сан",
        "reason": "қысқаша түсініктеме"
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=20)
        
        if response.status_code != 200:
            return {
                "error": "Gemini API error", 
                "status_code": response.status_code,
                "details": response.text,
                "tip": "Модель атауын немесе API Key-ді тексеріңіз"
            }

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            return {"error": "AI did not return valid JSON"}

        return json.loads(match.group(0))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- СКРИНШОТТЫ ТАЛДАУ (ЖАҢА) ---
@app.post("/analyze-screen")
def analyze_screen(request: ImageAnalysisRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    # Image-ге арналған ерекше prompt
    prompt = f"""
    Сен кибер-сарапшысың. Мына скриншотты мұқият тексер.
    Онда алаяқтық, фишинг, күмәнді сілтемелер, қауіпті батырмалар немесе басқа да зиянды белгілер бар ма?
    Пайдаланушыға қауіпті екенін түсіндір, егер қауіп болмаса, қауіпсіз деп айт.

    Жауапты ТЕК қана мына JSON форматында қайтар:
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "confidence": "0-100 арасындағы сан",
        "reason": "Скриншоттағы қауіпті/қауіпсіз белгілерді түсіндір"
    }}
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": request.image_base64}}
            ]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=60) # Сурет ауыр болғандықтан timeout-ты арттырдық
        
        if response.status_code != 200:
            print(f"Gemini Vision API Error: {response.text}")
            return {
                "error": "Gemini Vision API-мен байланыс үзілді",
                "details": response.json().get("error", {}).get("message", "Unknown error for image analysis"),
                "tip": "Gemini Vision API Key немесе модельді тексеріңіз"
            }

        data = response.json()
        # Жауап текстін алу
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            return {"error": "AI did not return valid JSON for image analysis"}

        return json.loads(match.group(0))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")