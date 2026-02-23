from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HF_TOKEN")
# Көптілді ең мықты модельдердің бірі
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

    # Санаттарды барынша нақты алаяқтыққа бағыттаймыз
    # "urgent scam" сөзі модельді сақ болуға мәжбүрлейді
    payload = {
        "inputs": msg.text,
        "parameters": {
            "candidate_labels": [
                "fraudulent scam money request", 
                "safe friendly chat"
            ]
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        if "error" in result:
             return {"error": "AI модель оянуда, 5 секундтан соң қайталаңыз..."}

        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        # Егер модель 'fraudulent' немесе 'scam' екеніне тіпті 30% сенімді болса - Қауіпті деп береміз
        is_scam = "scam" in top_label or "fraud" in top_label
        
        # Хакатон үшін сезімталдықты арттыру: 0.3 threshold
        if is_scam and top_score > 0.3:
            verdict = "Қауіпті"
            reason = "Алаяқтық белгілері анықталды"
        else:
            verdict = "Таза"
            reason = "Қауіпсіз хабарлама"
        
        return {
            "verdict": verdict,
            "confidence": f"{round(top_score * 100, 2)}%",
            "reason": reason,
            "ai_logic": top_label # Мұны презентацияда көрсетуге болады
        }
    except Exception as e:
        return {"error": str(e)}