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

# МОДЕЛЬ АТАУЫН ТҮЗЕТТІК (Ресми атауы осы)
GEMINI_MODEL = "gemini-2.0-flash-lite-preview-02-05"
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
    Ты кибер-эксперт по безопасности. Проанализируй текст на предмет мошенничества.
    Текст: "{msg.text}"
    Ответ верни СТРОГО в JSON формате:
    {{
        "verdict": "Қауіпті" или "Таза",
        "confidence": "число",
        "reason": "краткое объяснение"
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        # Vercel-де requests синхронды түрде жақсырақ жұмыс істейді
        response = requests.post(GEMINI_URL, json=payload, timeout=20)
        
        if response.status_code != 200:
            return {"error": "Gemini API error", "details": response.text}

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        # JSON-ды тазалап алу (Markdown-сыз)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            return {"error": "AI did not return valid JSON"}

        return json.loads(match.group(0))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))