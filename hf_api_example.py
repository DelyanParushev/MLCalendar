import requests
import os
from datetime import datetime, timedelta

# Hugging Face Inference API configuration
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
MODEL_ID = "dex7er999/NLPCalendar"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

def query_huggingface_api(text: str):
    """Query your model via Hugging Face Inference API"""
    if not HF_API_TOKEN:
        print("⚠️ Hugging Face API token not found")
        return None
        
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # For token classification (NER)
    data = {"inputs": text}
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Hugging Face API error: {e}")
        return None

def parse_text_with_hf_api(text: str) -> dict:
    """Parse text using Hugging Face Inference API"""
    
    # Try Hugging Face API first
    hf_result = query_huggingface_api(text)
    
    if hf_result:
        # Process HF API results to match your format
        return process_hf_results(text, hf_result)
    else:
        # Fallback to simple parsing
        return fallback_parse(text)

def process_hf_results(text: str, hf_result):
    """Convert HF API results to your calendar event format"""
    # This would process the token classification results
    # and extract title, date, time like your current parser
    
    # Simplified version for now
    return {
        "title": text.strip(),
        "datetime": datetime.now() + timedelta(days=1),
        "start": datetime.now() + timedelta(days=1),
        "end_datetime": None,
        "tokens": text.split(),
        "labels": ["O"] * len(text.split()),
        "debug": {"source": "huggingface_api"}
    }