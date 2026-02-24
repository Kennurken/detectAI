from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json
import re

app = FastAPI(title="Cyber-Detective API")

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

# Нақты жұмыс істейтін модель атауы
GEMINI_MODEL = "gemini-1.5-flash" 
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

@app.get("/")
def home():
    return {"status": "Cyber-Detective API Online", "model": GEMINI_MODEL}

# 1. МӘТІНДІ ТАЛДАУ
@app.post("/analyze")
def analyze(msg: Message):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = f"""
    Сен кибер-қауіпсіздік маманысың. Мына мәтінді алаяқтыққа (scam) талда:
    Текст: "{msg.text}"
    
    Жауапты ТЕК қана мына JSON форматында қайтар:
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "confidence": 0-100 арасындағы сан,
        "reason": "қысқаша түсініктеме"
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return call_gemini(payload)

# 2. СКРИНШОТТЫ ТАЛДАУ (Осы жер жетіспей тұрған еді!)
@app.post("/analyze-screen")
def analyze_screen(req: ImageRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = "Мына скриншотта алаяқтық (фишинг, жалған ұтыс, күмәнді сілтеме) бар ма? JSON форматында жауап бер: verdict (Қауіпті/Таза), confidence (0-100), reason (себебі)."

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": req.image_base64
                    }
                }
            ]
        }]
    }
    return call_gemini(payload)

# Gemini-мен байланыс функциясы
def call_gemini(payload):
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        if response.status_code != 200:
            return {"error": "API Error", "details": response.text}

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            return {"error": "AI did not return valid JSON", "raw": raw_text}
            
        return json.loads(match.group(0))
    except Exception as e:
        return {"error": str(e)}