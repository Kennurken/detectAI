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
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

class URLRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "Cyber-Detective API Online", "model": GEMINI_MODEL}

# 1. СІЛТЕМЕНІ ТАЛДАУ (URL)
@app.post("/analyze-url")
def analyze_url(req: URLRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = f"""
    Сен кибер-қауіпсіздік маманысың. Мына сілтемені (URL) фишингке тексер: "{req.url}"
    
    Ережелер:
    1. Шешімің қауіпсіз болса "verdict": "Таза", қауіпті болса "Қауіпті" деп жаз.
    2. "confidence": Өз шешіміңе қаншалықты сенімдісің? (0-100 арасында сан). Мысалы, ресми сайт болса 100 деп бер.
    3. "reason": Қысқаша қазақша түсіндірме.
    
    Жауапты ТЕК JSON форматында қайтар.
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return call_gemini(payload)

# 2. МӘТІНДІ ТАЛДАУ (Text)
@app.post("/analyze")
def analyze(msg: Message):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = f"""
    Мына мәтінді алаяқтыққа талда: "{msg.text}"
    
    Жауап форматы (JSON):
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "confidence": 0-100 (сенімділік деңгейі),
        "reason": "себебі"
    }}
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return call_gemini(payload)

# 3. СКРИНШОТТЫ ТАЛДАУ (Vision)
@app.post("/analyze-screen")
def analyze_screen(req: ImageRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = "Мына скриншотты талда. Алаяқтық белгілері бар ма? JSON форматында жауап бер: verdict (Қауіпті/Таза), confidence (0-100), reason (қазақша түсініктеме)."

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
            return {"error": "API error", "status": response.status_code}

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            return {"error": "Invalid AI response"}
            
        return json.loads(match.group(0))
    except Exception as e:
        return {"error": str(e)}