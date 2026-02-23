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

    # Бұл жерде біз модельге "не іздеу керек" екенін нақты айтамыз.
    # "financial scam" және "money request" сөздері алаяқтықты табуға көмектеседі.
    payload = {
        "inputs": msg.text,
        "parameters": {
            "candidate_labels": [
                "fraudulent money scam request", 
                "legitimate friendly conversation"
            ]
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        if "error" in result:
             return {"error": "AI модель оянуда, 5 секундтан соң қайталаңыз..."}

        # Нәтижелерді алу
        labels = result.get("labels", [])
        scores = result.get("scores", [])
        
        if not labels:
            return {"error": "AI-дан жауап келмеді"}

        top_label = labels[0]
        top_score = scores[0]
        
        # Егер ең бірінші таңдалған санат "fraudulent" (алаяқтық) болса, 
        # тіпті оның ұпайы 30% (0.3) болса да, біз оны Қауіпті деп белгілейміз.
        is_scam = "fraudulent" in top_label
        
        # Шекті барынша төмендеттік (0.3), себебі бізге "өте сақ" детектив керек
        if is_scam and top_score > 0.3:
            verdict = "Қауіпті"
            reason = "Алаяқтық белгілері анықталды (күдікті ақша сұрау)"
        else:
            verdict = "Таза"
            reason = "Қауіпсіз хабарлама"
        
        return {
            "verdict": verdict,
            "confidence": f"{round(top_score * 100, 2)}%",
            "reason": reason,
            "debug": top_label # Бұл модельдің іштей не таңдағанын көру үшін
        }
    except Exception as e:
        return {"error": str(e)}