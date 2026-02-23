from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# --- CORS рұқсатын қосу ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Барлық жерден сұраныс қабылдауға рұқсат береді
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/symanto/xlm-roberta-base-snli-mnli"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Cyber-Detective API is online"}

@app.post("/analyze")
def analyze(msg: Message):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN missing"}

    # Көптілді модель үшін мағыналы санаттар
    payload = {
        "inputs": msg.text,
        "parameters": {
            "candidate_labels": ["suspicious scam or fraud", "normal safe conversation"]
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        if "error" in result:
             return {"error": "AI модель оянуда, 5 секундтан соң қайталаңыз..."}

        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        # Егер модель 'scam' екеніне сенімді болса
        is_fraud = "scam" in top_label
        
        # Хакатонда эффект болуы үшін: егер сенімділік 40%-дан асса, күдікті деп атаймыз
        verdict = "Қауіпті" if (is_fraud and top_score > 0.4) else "Таза"
        
        return {
            "verdict": verdict,
            "confidence": f"{round(top_score * 100, 2)}%",
            "reason": "Алаяқтық белгілері" if verdict == "Қауіпті" else "Қауіпсіз хабарлама"
        }
    except Exception as e:
        return {"error": str(e)}