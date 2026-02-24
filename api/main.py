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

# СЕН СҰРАҒАН МОДЕЛЬ: gemini-2.5-flash-lite
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str
class URLRequest(BaseModel):
    url: str

@app.post("/analyze-url")
def analyze_url(req: URLRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = f"""
    Сен кибер-қауіпсіздік маманысың. Мына сілтемені (URL) фишинг немесе алаяқтыққа тексер:
    Сілтеме: "{req.url}"
    
    Жауапты ТЕК қана мына JSON форматында қайтар:
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "confidence": 0-100,
        "reason": "қысқаша түсініктеме (мысалы: домен күмәнді немесе ресми сайтқа ұқсайды)"
    }}
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return call_gemini(payload)

@app.get("/")
def home():
    return {"status": "Cyber-Detective API Online", "model": GEMINI_MODEL}

# 1. МӘТІНДІ ТАЛДАУ (Ескі функция сақталды)
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
        "confidence": 0,
        "reason": "қысқаша түсініктеме"
    }}
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return call_gemini(payload)

# 2. СКРИНШОТТЫ ТАЛДАУ (Жаңа қосылған функция)
@app.post("/analyze-screen")
def analyze_screen(req: ImageRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing")

    prompt = "Мына скриншотты талда. Егер алаяқтық болса 'Қауіпті', болмаса 'Таза' деп жауап бер. Формат ТЕК JSON: verdict, confidence (0-100), reason."

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

# Ортақ жіберу функциясы
def call_gemini(payload):
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {
                "error": "Gemini API error",
                "status": response.status_code,
                "details": response.json()
            }

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # JSON-ды мәтін ішінен тауып алу
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            return {"error": "AI did not return valid JSON", "text": raw_text}
            
        return json.loads(match.group(0))
    except Exception as e:
        return {"error": str(e)}