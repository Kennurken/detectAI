from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Message(BaseModel):
    text: str

@app.post("/analyze")
def analyze(msg: Message):
    if not OPENAI_API_KEY:
        return {"error": "OpenAI API Key missing"}

    # GPT-ге нақты нұсқаулық (Prompt) береміз
    prompt = f"""
    Сен кибер-қауіпсіздік маманысың. Мына мәтінді талдап, оның алаяқтық (scam) екенін анықта:
    "{msg.text}"
    
    Жауапты қатаң түрде мына JSON форматында қайтар:
    {{
        "verdict": "Қауіпті" немесе "Таза",
        "confidence": "0-100% арасында",
        "reason": "Қысқаша себебі"
    }}
    """

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        res_data = response.json()
        
        # GPT-ден келген мәтінді (JSON-ды) оқу
        import json
        ai_response = json.loads(res_data['choices'][0]['message']['content'])
        
        return ai_response
    except Exception as e:
        return {"error": str(e)}