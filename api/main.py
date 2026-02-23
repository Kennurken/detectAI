from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# 1. Токенді жасырын түрде алу (Vercel-дегі HF_TOKEN айнымалысынан оқиды)
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Cyber-Detective API is online", "model": "BART-Large-MNLI"}

@app.post("/analyze")
def analyze(msg: Message):
    # API токенінің бар-жоғын тексеру
    if not HF_TOKEN:
        return {"error": "HF_TOKEN табылған жоқ. Vercel-де Environment Variable ретінде қосыңыз."}

    # Алаяқтық санаттарын анықтауға арналған сұраныс
    payload = {
        "inputs": msg.text,
        "parameters": {"candidate_labels": ["fraud", "drugs", "spam", "safe", "illegal service"]}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        # Егер Hugging Face қате жіберсе немесе модель әлі жүктелмесе
        if "error" in result:
             return {"error": "Model is loading, please try again in a few seconds.", "details": result["error"]}

        # Нәтижелерді талдау
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        # Қауіптілік деңгейін анықтау: егер ең жоғарғы санат 'safe' емес болса
        # немесе 'safe' деңгейі тым төмен болса (мысалы 0.4-тен аз)
        is_safe = top_label == "safe" and top_score > 0.5
        
        return {
            "text": msg.text,
            "verdict": "Таза" if is_safe else "Қауіпті",
            "reason": top_label if not is_safe else "Normal text",
            "confidence": f"{round(top_score * 100, 2)}%",
            "full_analysis": {
                "labels": result.get("labels"),
                "scores": [f"{round(s * 100, 2)}%" for s in result.get("scores")]
            }
        }
    except Exception as e:
        return {"error": "Сервермен байланыс кезінде қате шықты", "details": str(e)}