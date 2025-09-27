# ml/backend_api.py

from fastapi import FastAPI
from pydantic import BaseModel
from ml.nlp_parser_ml import parse_calendar_event
import uvicorn

# -----------------------------
# FastAPI приложение
# -----------------------------
app = FastAPI(title="Calendar NER API", description="API за извличане на събития от текст")

# -----------------------------
# Pydantic модел за вход
# -----------------------------
class TextInput(BaseModel):
    text: str

# -----------------------------
# POST endpoint за inference
# -----------------------------
@app.post("/parse/")
def parse_event(payload: TextInput):
    """
    Взима JSON с ключ "text" и връща токени + предсказани етикети
    """
    text = payload.text
    return parse_calendar_event(text)

# -----------------------------
# Стартиране на локален сървър
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("ml.backend_api:app", host="0.0.0.0", port=8000, reload=True)
