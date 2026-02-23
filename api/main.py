from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Hugging Face-тен алған токенді осы жерге қоясың (немесе Vercel Environment Variables-ке сал)
HF_TOKEN = "СЕНІҢ_ТОКЕНІҢ" 
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

class Message(BaseModel):
    text: str

@app.post("/analyze")
def analyze(msg: Message):
    # Алаяқтық санаттарын анықтау
    payload = {
        "inputs": msg.text,
        "parameters": {"candidate_labels": ["fraud", "drugs", "spam", "safe", "illegal service"]}
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()
    
    # Қарапайым логика: егер 'safe' емес санаттардың пайызы жоғары болса
    return {
        "text": msg.text,
        "labels": result.get("labels"),
        "scores": result.get("scores"),
        "verdict": "Қауіпті" if result["labels"][0] != "safe" else "Таза"
    }