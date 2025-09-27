# ml/test_inference.py
import torch
from transformers import BertTokenizerFast, BertForTokenClassification
import os

# Път до папката с тренирания модел
MODEL_DIR = "ml/model"

# Зареждане на токенизатор и модел
tokenizer = BertTokenizerFast.from_pretrained(MODEL_DIR)
model = BertForTokenClassification.from_pretrained(MODEL_DIR)

# Етикети от модела (в същия ред, както при тренировката)
LABELS = ['B-PERSON', 'B-PLACE', 'B-TITLE', 'B-WHEN_DAY', 'B-WHEN_START', 'I-WHEN_DAY', 'O']

# Функция за inference върху един текст
def predict(text):
    # Токенизация
    encoding = tokenizer(text.split(),  # сплитваме по space, за да имаме същите "tokens"
                         is_split_into_words=True,
                         return_tensors="pt",
                         truncation=True,
                         padding=True)
    
    input_ids = encoding["input_ids"]
    attention_mask = encoding["attention_mask"]

    # Модел предсказание
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1).squeeze().tolist()

    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze())
    
    # Map към оригиналните токени
    word_ids = encoding.word_ids(batch_index=0)
    token_labels = []
    current_word_idx = None
    for idx, word_idx in enumerate(word_ids):
        if word_idx is None:
            continue
        if word_idx != current_word_idx:
            current_word_idx = word_idx
            token_labels.append(LABELS[predictions[idx]])
    
    result = {
        "tokens": text.split(),
        "labels": token_labels
    }
    return result

# Пример за тест
if __name__ == "__main__":
    examples = [
        "Обяд от 15 събота с приятели",
        "Вечеря в 18 петък в парка",
        "Университет от 10 утре"
    ]
    
    for ex in examples:
        pred = predict(ex)
        print(pred)
