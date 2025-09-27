import json
from pathlib import Path
from datasets import Dataset
import evaluate
from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments

# --- Настройки ---
MODEL_NAME = "bert-base-multilingual-cased"
DATA_DIR = Path("ml/data")
OUTPUT_DIR = Path("ml/model")
BATCH_SIZE = 8
EPOCHS = 5
LEARNING_RATE = 5e-5
MAX_LENGTH = 128

# --- Зареждане на данни ---
def load_jsonl(file_path):
    examples = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            examples.append(json.loads(line))
    return examples

train_data = load_jsonl(DATA_DIR / "train.jsonl")
dev_data = load_jsonl(DATA_DIR / "dev.jsonl")
test_data = load_jsonl(DATA_DIR / "test.jsonl")

# --- Етикети ---
labels = ["B-PERSON","B-PLACE","B-TITLE","B-WHEN_DAY","B-WHEN_START","I-WHEN_DAY","O"]
label2id = {l:i for i,l in enumerate(labels)}
id2label = {i:l for l,i in label2id.items()}

# --- Tokenizer ---
tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)

def encode_examples(examples):
    tokenized_inputs = tokenizer(examples["tokens"], is_split_into_words=True, truncation=True, padding="max_length", max_length=MAX_LENGTH)
    all_labels = []
    for i, label in enumerate(examples["labels"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = []
        for word_id in word_ids:
            if word_id is None:
                label_ids.append(-100)
            else:
                label_ids.append(label2id[label[word_id]])
        all_labels.append(label_ids)
    tokenized_inputs["labels"] = all_labels
    return tokenized_inputs

# --- Dataset към HuggingFace ---
def convert_to_dataset(data_list):
    texts = [d["tokens"] for d in data_list]
    labels_list = [d["labels"] for d in data_list]
    ds = Dataset.from_dict({"tokens": texts, "labels": labels_list})
    ds = ds.map(encode_examples, batched=True)
    return ds

train_ds = convert_to_dataset(train_data)
eval_ds = convert_to_dataset(dev_data)

# --- Модел ---
model = BertForTokenClassification.from_pretrained(MODEL_NAME, num_labels=len(labels))

# --- TrainingArguments (за Transformers 4.55.2) ---
args = TrainingArguments(
    output_dir=str(OUTPUT_DIR),
    do_train=True,
    do_eval=True,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    weight_decay=0.01,
    logging_dir=str(OUTPUT_DIR / "logs"),
    logging_steps=10,
    save_total_limit=2,
    save_steps=100
)

# --- Метрика за evaluation  ---
metric = evaluate.load("seqeval")

def compute_metrics(p):
    predictions, labels = p
    predictions = predictions.argmax(axis=-1)
    true_labels = [[id2label[l] for l in label if l != -100] for label in labels]
    true_preds = [[id2label[p] for (p,l) in zip(pred, label) if l != -100] for pred,label in zip(predictions,labels)]
    results = metric.compute(predictions=true_preds, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }

# --- Trainer ---
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=eval_ds,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# --- Стартиране на тренировката ---
trainer.train()

# --- Запазване на модела и токенизатора ---
trainer.save_model(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))

# --- Запазване на етикетите ---
with open(OUTPUT_DIR / "labels.json", "w", encoding="utf-8") as f:
    json.dump(labels, f, ensure_ascii=False, indent=2)
