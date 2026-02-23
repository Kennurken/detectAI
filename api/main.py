from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, requests, json, re

app = FastAPI()

# --- CORS БАПТАУЫН КҮШЕЙТУ ---
# allow_origins=["*"] - бұл кеңейтілімдер үшін маңызды
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Preflight (OPTIONS) сұраныстарын қолмен өңдеу (браузер блоктамауы үшін)
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        },
    )

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"
# API нұсқасын v1beta-дан v1-ге ауыстыру тұрақтылықты арттыруы мүмкін
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

def get_ai_response(payload):
    if not GEMINI_API_KEY:
        return {"error": "API Key табылмады. Vercel-де айнымалыны орнатыңыз."}
    
    try:
        # Timeout-ты 30 секундқа қалдырамыз, Vision үшін маңызды
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {"error": f"Gemini API Error {response.status_code}", "details": response.text}
        
        data = response.json()
        
        if "candidates" not in data or not data["candidates"]:
            return {"error": "AI жауап бермеді (Safety block немесе қате)"}
            
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Маркдаунды (```json ... ```) алып тастап, тек ішіндегі JSON-ды алу
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        return {"error": "AI жауабы JSON форматында емес", "raw": raw_text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def health_check():
    return {"status": "online", "model": GEMINI_MODEL}

@app.post("/analyze")
async def analyze(msg: Message):
    # Промптты күшейттік: алаяқтықтың нақты белгілерін іздеуді тапсырдық
    prompt = (
        f"Сен тәжірибелі кибер-қауіпсіздік сарапшысысың. Мына мәтінді талда: '{msg.text}'. "
        "Мәтінде алаяқтық, фишинг, күдікті сілтемелер немесе манипуляция бар ма? "
        "Жауапты қатаң түрде ТЕК осы JSON форматында бер: "
        '{"verdict": "Қауіпті/Таза", "confidence": 0-100, "reason": "неліктен бұлай шештің?"}'
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return get_ai_response(payload)

@app.post("/analyze-screen")
async def analyze_screen(req: ImageRequest):
    prompt = (
        "Мына скриншотты талда. Бұл жерде фишингтік сайт, жалған банк қосымшасы немесе "
        "күдікті хабарлама бар ма? "
        "Жауапты қатаң түрде ТЕК осы JSON форматында бер: "
        '{"verdict": "Қауіпті/Таза", "confidence": 0-100, "reason": "негізгі себебі"}'
    )
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": req.image_base64}}
            ]
        }]
    }
    return get_ai_response(payload)