from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json
import re

app = FastAPI(title="Digital Trace AI API")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- CONFIG --------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# МОДЕЛЬ АТАУЫН ТҮЗЕТТІК: gemini-2.0-flash (қазіргі ең жылдамы)
GEMINI_MODEL = "gemini-2.5-flash-lite" 
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Деректер модельдері
class URLRequest(BaseModel):
    url: str

class ImageRequest(BaseModel):
    image_base64: str

@app.get("/")
def home():
    return {"status": "Digital Trace AI Online", "model": GEMINI_MODEL}

# 1. СІЛТЕМЕНІ ЖӘНЕ МӘТІНДІ ТАЛДАУ (/check)
@app.post("/check")
def check_content(req: URLRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = f"""
    Сен Digital Trace AI жүйесісің. Мына сілтемені немесе мәтінді фишингке/алаяқтыққа тексер: "{req.url}"
    Жауапты ТЕК JSON форматында қайтар:
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "scam_score": 0-100,
        "detail": "Қысқаша қазақша түсіндірме"
    }}
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return call_gemini(payload)

# 2. ЭКРАНДЫ (СКРИНШОТТЫ) ТАЛДАУ (/analyze-screen)
@app.post("/analyze-screen")
def analyze_screen(req: ImageRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    # Vision үшін арнайы промпт
    prompt = "Сен Digital Trace AI жүйесісің. Мына скриншотты талда. Алаяқтық белгілері, фишингтік сайт немесе күмәнді хабарлама бар ма? Жауапты ТЕК JSON форматында бер: verdict (Қауіпті/Таза), scam_score (0-100), detail (қазақша түсіндірме)."

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": req.image_base64}}
            ]
        }]
    }
    return call_gemini(payload)

# Ортақ жіберу функциясы
def call_gemini(payload):
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {"error": "API error", "status": response.status_code, "msg": response.text}

        data = response.json()
        
        if "candidates" not in data or not data["candidates"]:
            return {"error": "AI жауап бермеді", "raw": data}

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # JSON-ды мәтін ішінен тауып алу
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        
        if match:
            res = json.loads(match.group(0))
            return {
                "verdict": res.get("verdict", "Белгісіз"),
                "scam_score": res.get("scam_score", res.get("confidence", 0)),
                "detail": res.get("detail", res.get("reason", "Талдау аяқталды"))
            }
        return {"error": "AI жауабы форматқа сай емес"}
    except Exception as e:
        return {"error": str(e)}