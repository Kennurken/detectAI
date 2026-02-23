from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, json, re

app = FastAPI()

# Кез келген жерден келетін сұранысқа рұқсат беру
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Модель атын тұрақты v1beta нұсқасына қойдық
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

class Message(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

# Жауапты CORS header-лерімен қайтару функциясы
def prepare_response(data):
    return JSONResponse(
        content=data,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

from fastapi.responses import JSONResponse

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return prepare_response({"status": "ok"})

@app.get("/")
def health():
    return prepare_response({"status": "online"})

@app.post("/analyze")
async def analyze(msg: Message):
    prompt = f"Талдау жаса: {msg.text}. Жауапты тек JSON: {{\"verdict\": \"Таза/Қауіпті\", \"confidence\": 90, \"reason\": \"себебі\"}}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(GEMINI_URL, json=payload, timeout=15)
        data = res.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        return prepare_response(json.loads(match.group(0)) if match else {"error": "AI failure"})
    except Exception as e:
        return prepare_response({"error": str(e)})

@app.post("/analyze-screen")
async def analyze_screen(req: ImageRequest):
    prompt = "Скриншотта фишинг бар ма? Жауапты тек JSON: {\"verdict\": \"Таза/Қауіпті\", \"confidence\": 90, \"reason\": \"себебі\"}"
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": req.image_base64}}
            ]
        }]
    }
    try:
        res = requests.post(GEMINI_URL, json=payload, timeout=20)
        data = res.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        return prepare_response(json.loads(match.group(0)) if match else {"error": "AI failure"})
    except Exception as e:
        return prepare_response({"error": str(e)})