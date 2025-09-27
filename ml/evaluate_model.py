import json
from datasets import Dataset
import evaluate
from transformers import BertTokenizerFast, BertForTokenClassification, Trainer

# --- Конфигурация ---
MODEL_DIR = "ml/model"        # папката с тренирания модел
TEST_DATA_PATH = "ml/data/test.jsonl"

# --- Зареждане на токенизатор и модел ---
tokenizer = BertTokenizerFast.from_pretrained(MODEL_DIR)
model = BertForTokenClassification.from_pretrained(MODEL_DIR)

# --- Зареждане на тест сет ---
def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

test_data = load_jsonl(TEST_DATA_PATH)
label_list = ['B-PERSON', 'B-PLACE', 'B-TITLE', 'B-WHEN_DAY', 'B-WHEN_START', 'I-WHEN_DAY', 'O']
label2id = {l: i for i, l in enumerate(label_list)}
id2label = {i: l for i, l in enumerate(label_list)}

def encode_labels(example):
    example["labels"] = [label2id[l] for l in example["labels"]]
    return example

def tokenize_and_align_labels(example):
    tokenized = tokenizer(
        example["tokens"],
        truncation=True,
        padding="max_length",  # <-- add this line
        is_split_into_words=True,
        max_length=64,
    )
    word_ids = tokenized.word_ids()
    label_ids = []
    previous_word_idx = None
    for word_idx in word_ids:
        if word_idx is None:
            label_ids.append(-100)
        elif word_idx != previous_word_idx:
            label_ids.append(example["labels"][word_idx])
        else:
            label_ids.append(-100)
        previous_word_idx = word_idx
    tokenized["labels"] = label_ids
    return tokenized

# --- Преобразуване на labels и токенизация ---
dataset = Dataset.from_list(test_data)
dataset = dataset.map(encode_labels)
dataset = dataset.map(tokenize_and_align_labels)

# --- Metric setup ---
metric = evaluate.load("seqeval")  # seqeval работи за токеново NER
def compute_metrics(p):
    predictions, labels = p
    predictions = predictions.argmax(axis=-1)

    true_predictions = [
        [id2label[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [id2label[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    results = metric.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"]
    }

# --- Trainer за evaluation ---
trainer = Trainer(
    model=model,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# --- Evaluation ---
results = trainer.evaluate(dataset)
print("=== Evaluation results ===")
for k, v in results.items():
    print(f"{k}: {v:.4f}")