from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, requests, json, re

app = FastAPI()

# --- CORS БАПТАУЫН КҮШЕЙТУ ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Кеңейтілімдер үшін осылай қалдырған дұрыс
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # OPTIONS міндетті түрде керек
    allow_headers=["*"],
)

# Кеңейтілімнен келетін Preflight сұраныстарды қолмен өңдеу (CORS қатесін болдырмау үшін)
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

def get_ai_response(payload):
    if not GEMINI_API_KEY:
        return {"error": "API Key табылмады. Vercel Environment Variables тексеріңіз."}
    
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        
        # API-дан қате келсе, толық мәтінді көру (debug үшін)
        if response.status_code != 200:
            print(f"Gemini Error: {response.text}")
            return {"error": f"Gemini API Error {response.status_code}", "details": response.text}
        
        data = response.json()
        
        # Жауап құрылымын тексеру
        if "candidates" not in data or not data["candidates"]:
            return {"error": "AI жауап бермеді", "details": data}
            
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # JSON-ды тазалап алу (AI кейде маркдаунмен береді)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        return {"error": "AI жауапты JSON форматында бермеді", "raw": raw_text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def health_check():
    return {"status": "online", "model": GEMINI_MODEL}

@app.post("/analyze")
async def analyze(msg: Message):
    prompt = f"Сен кибер-сарапшысың. Мына мәтінді алаяқтыққа (scam/phishing) талда: '{msg.text}'. Жауапты ТЕК қана мына JSON форматында бер: {{\"verdict\": \"Қауіпті/Таза\", \"confidence\": 0-100, \"reason\": \"себебі\"}}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return get_ai_response(payload)

@app.post("/analyze-screen")
async def analyze_screen(req: ImageRequest):
    prompt = "Мына скриншотты кибер-қауіпсіздік тұрғысынан талда. Алаяқтық, фишинг немесе күдікті батырмалар бар ма? Жауапты ТЕК қана мына JSON форматында бер: {{\"verdict\": \"Қауіпті/Таза\", \"confidence\": 0-100, \"reason\": \"себебі\"}}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": req.image_base64}}
            ]
        }]
    }
    return get_ai_response(payload)