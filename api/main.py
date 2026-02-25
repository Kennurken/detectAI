from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json
import re

app = FastAPI(title="Digital Trace AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# КОНФИГУРАЦИЯ
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3-flash" 
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class URLRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "Digital Trace AI Online", "model": GEMINI_MODEL}

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

def call_gemini(payload):
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        if response.status_code != 200:
            return {"error": "API error", "status": response.status_code, "msg": response.text}

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        
        if match:
            res = json.loads(match.group(0))
            return {
                "verdict": res.get("verdict", "Белгісіз"),
                "scam_score": res.get("scam_score", res.get("confidence", 0)),
                "detail": res.get("detail", res.get("reason", ""))
            }
        return {"error": "Invalid AI response format"}
    except Exception as e:
        return {"error": str(e)}