from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, requests, json, re

app = FastAPI()

# 1. CORS Middleware - Барлық сұранысқа рұқсат
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. CORS Preflight Header-лерді автоматты қосатын функция
def cors_response(content):
    return JSONResponse(
        content=content,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

# Бұл жерде модель атын өзгерттім: gemini-2.0-flash қазіргі ең жылдамы
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite" 
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

def get_ai_response(payload):
    if not GEMINI_API_KEY:
        return {"error": "API Key табылмады."}
    
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {"error": f"API Error {response.status_code}", "details": response.text}
        
        data = response.json()
        if "candidates" not in data or not data["candidates"]:
            return {"error": "AI жауап бермеді (Safety block)"}
            
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # JSON-ды мәтін ішінен тауып алу
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        return {"error": "JSON табылмады", "raw": raw_text}
    except Exception as e:
        return {"error": str(e)}

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return cors_response({"status": "ok"})

@app.get("/")
def health_check():
    return cors_response({"status": "online", "model": GEMINI_MODEL})

@app.post("/analyze")
async def analyze(msg: Message):
    prompt = (
        f"Сен кибер-қауіпсіздік сарапшысысың. Мына мәтінді талда: '{msg.text}'. "
        "Жауапты ТЕК JSON форматында бер: "
        '{"verdict": "Қауіпті/Таза", "confidence": 0-100, "reason": "себебі"}'
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    result = get_ai_response(payload)
    return cors_response(result)

@app.post("/analyze-screen")
async def analyze_screen(req: ImageRequest):
    prompt = (
        "Скриншотта фишинг немесе алаяқтық бар ма? "
        "Жауапты ТЕК JSON форматында бер: "
        '{"verdict": "Қауіпті/Таза", "confidence": 0-100, "reason": "себебі"}'
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": req.image_base64}}
            ]
        }]
    }
    result = get_ai_response(payload)
    return cors_response(result)