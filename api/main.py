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
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
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

    payload = {
        "inputs": msg.text,
        "parameters": {"candidate_labels": ["fraud", "drugs", "spam", "safe", "illegal service"]}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        # Егер модель әлі жүктеліп жатса (warming up)
        if "error" in result:
             return {"error": "AI model is warming up, try again in 5s"}

        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        # Қарапайым логика: егер 'safe' деңгейі 0.5-тен жоғары болса — Таза
        is_safe = top_label == "safe" and top_score > 0.5
        
        return {
            "verdict": "Таза" if is_safe else "Қауіпті",
            "confidence": f"{round(top_score * 100, 2)}%",
            "reason": top_label if not is_safe else "Normal"
        }
    except Exception as e:
        return {"error": str(e)}