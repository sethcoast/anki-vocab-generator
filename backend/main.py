# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.pipeline import process_vocab_word

app = FastAPI()

class CardRequest(BaseModel):
    word: str
    target_lang: str = "ja"
    base_lang: str = "en"

@app.post("/generate-card")
def generate_card_endpoint(req: CardRequest):
    try:
        result = process_vocab_word(req.word, req.target_lang, req.base_lang)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
