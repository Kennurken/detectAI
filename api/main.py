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

# СЕН СҰРАҒАН МОДЕЛЬ АТАУЫ (Gemini 2.5 Flash Lite)
# Егер 404 қатесін берсе, атауын "gemini-2.5-flash-lite-preview" деп көруге болады
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Cyber-Detective API Online", "model": GEMINI_MODEL}

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
        "confidence": "0-100 арасындағы сан",
        "reason": "қысқаша түсініктеме"
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=20)
        
        # Егер модель табылмаса немесе API қате берсе
        if response.status_code != 200:
            return {
                "error": "Gemini API error", 
                "status_code": response.status_code,
                "details": response.text,
                "tip": "Модель атауын немесе API Key-ді тексеріңіз"
            }

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        # JSON-ды Markdown-сыз тазалап алу
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            return {"error": "AI did not return valid JSON"}

        return json.loads(match.group(0))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))