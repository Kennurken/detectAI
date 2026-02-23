from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, json, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# СЕН СҰРАҒАН МОДЕЛЬ (Скриншот бойынша)
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

def get_ai_response(payload):
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        if response.status_code != 200:
            return {"error": f"API Error {response.status_code}", "details": response.text}
        
        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # JSON тазалау логикасы
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"error": "AI-дан JSON форматы келмеді", "raw": raw_text}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze")
def analyze(msg: Message):
    prompt = f"Сен кибер-сарапшысың. Мына мәтінді алаяқтыққа талда: '{msg.text}'. Жауапты ТЕК JSON форматында бер: {{\"verdict\": \"Қауіпті/Таза\", \"confidence\": 0-100, \"reason\": \"себебі\"}}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return get_ai_response(payload)

@app.post("/analyze-screen")
def analyze_screen(req: ImageRequest):
    prompt = "Мына скриншотты кибер-қауіпсіздік тұрғысынан талда. Алаяқтық, фишинг немесе күдікті әрекет бар ма? Жауапты ТЕК JSON форматында бер: {{\"verdict\": \"Қауіпті/Таза\", \"confidence\": 0-100, \"reason\": \"себебі\"}}"
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": req.image_base64}}
            ]
        }]
    }
    return get_ai_response(payload)