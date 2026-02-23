from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Gemini 2.5 Flash-Lite - ең соңғы, жеңіл әрі ақылды модель
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite-preview-02-05:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Cyber-Detective API is online with Gemini 2.0 Flash-Lite"}

@app.post("/analyze")
def analyze(msg: Message):
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY missing"}

    # Нұсқаулықты қаталдау жаздық, себебі 2.0 нұсқасы логиканы жақсы түсінеді
    prompt = f"""
    Сен кибер-қауіпсіздік маманысың. Мына мәтінді талдап, оның алаяқтық (scam) екенін анықта:
    "{msg.text}"
    
    Жауапты ТЕК қана мына JSON форматында қайтар (басқа артық сөз жазба):
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "confidence": "пайыз көрсеткіші",
        "reason": "Қысқаша себебі"
    }}
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        res_data = response.json()
        
        # Модель жауабын өңдеу
        raw_content = res_data['candidates'][0]['content']['parts'][0]['text']
        # Markdown белгілерін (```json) тазалау
        clean_json = raw_content.replace('```json', '').replace('```', '').strip()
        
        ai_response = json.loads(clean_json)
        return ai_response
    except Exception as e:
        return {"error": f"Gemini 2.0 Error: {str(e)}"}