import json
import random
import os

# Папка за данни
os.makedirs("ml/data", exist_ok=True)

# Шаблони за примери
titles = ["Обяд", "Вечеря", "Среща", "Футбол", "Кино", "Разходка"]
persons = ["Иван", "Мария", "Гери", "Петър", "Ники"]
places = ["парка", "офиса", "къщи", "заведението", "стадион"]
days = ["понеделник", "вторник", "сряда", "четвъртък", "петък", "събота", "неделя"]
times = ["15", "16", "17", "18", "19", "20", "21"]

examples = []

for _ in range(500):  # общ брой примери
    title = random.choice(titles)
    person = random.choice(persons)
    place = random.choice(places)
    day = random.choice(days)
    time = random.choice(times)

    # различни варианти на изречения
    variants = [
        ([title, "от", time, day, "с", person],
         ["B-TITLE", "O", "B-WHEN_START", "B-WHEN_DAY", "O", "B-PERSON"]),
        ([title, "от", time, day, "в", place],
         ["B-TITLE", "O", "B-WHEN_START", "B-WHEN_DAY", "O", "B-PLACE"]),
        (["В", day, "от", time, title, "с", person],
         ["B-WHEN_DAY", "I-WHEN_DAY", "O", "B-WHEN_START", "B-TITLE", "O", "B-PERSON"]),
        (["На", f"{random.randint(1,28)}ти", "от", time, title],
         ["O", "B-WHEN_DAY", "O", "B-WHEN_START", "B-TITLE"]),
    ]

    tokens, labels = random.choice(variants)

    # гаранция, че няма да пишем невалидни
    if len(tokens) != len(labels):
        continue

    examples.append({"tokens": tokens, "labels": labels})

# Разделяне на train/dev/test
random.shuffle(examples)
n_total = len(examples)
n_train = int(0.7 * n_total)
n_dev = int(0.15 * n_total)

train = examples[:n_train]
dev = examples[n_train:n_train+n_dev]
test = examples[n_train+n_dev:]

def write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for ex in data:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

write_jsonl("ml/data/train.jsonl", train)
write_jsonl("ml/data/dev.jsonl", dev)
write_jsonl("ml/data/test.jsonl", test)

print(f"Генерирани: {len(train)} train, {len(dev)} dev, {len(test)} test")
