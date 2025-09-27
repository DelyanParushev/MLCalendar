import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

# Зареждаме модела и tokenizer
model_path = "ml/model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)

# Зареждаме етикетите
with open("ml/labels.txt", "r", encoding="utf-8") as f:
    labels = [line.strip() for line in f.readlines()]

def predict_sentence(sentence):
    tokens = tokenizer(sentence, return_tensors="pt", is_split_into_words=False)
    with torch.no_grad():
        outputs = model(**tokens)
    
    predictions = torch.argmax(outputs.logits, dim=2)
    token_ids = tokens["input_ids"][0]
    word_ids = tokens.word_ids(batch_index=0)

    word_predictions = {}
    for idx, word_id in enumerate(word_ids):
        if word_id is None:
            continue
        label = labels[predictions[0, idx].item()]
        if word_id in word_predictions:
            # ако има subwords, вземаме първия етикет
            continue
        word_predictions[word_id] = label
    
    # Възстановяване на думите
    words = []
    for word_id in sorted(word_predictions.keys()):
        word = tokenizer.convert_ids_to_tokens(token_ids)[tokens.word_ids(batch_index=0).index(word_id)]
        word = word.replace("##", "")  # премахваме subword маркера
        words.append((word, word_predictions[word_id]))
    
    return words

# Примерни изречения
sentences = [
    "Обяд от 15 събота с приятели",
    "Среща в 18 петък в парка",
    "Киното е в 20 вечерта"
]

for sent in sentences:
    print(f"\nSentence: {sent}")
    result = predict_sentence(sent)
    for word, label in result:
        print(f"{word}\t-> {label}")
