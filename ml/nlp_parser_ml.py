# ml/nlp_parser_ml.py
import re
import json
from datetime import datetime, timedelta, time, date
from typing import Optional, Tuple

import torch
from transformers import BertTokenizerFast, BertForTokenClassification

# !!! ВАЖНО: относителният път е спрямо ТЕКУЩАТА РАБОТНА ДИРЕКТОРИЯ
# ако стартираш uvicorn от корена (calendar-ai), това е правилно.
# ако стартираш от backend/, смени на "../ml/model"
MODEL_DIR = "ml/model"

# Зареждане на токенизатор и модел (ТВОЯТ обучен модел)
tokenizer = BertTokenizerFast.from_pretrained(MODEL_DIR)
model = BertForTokenClassification.from_pretrained(MODEL_DIR)
model.eval()

# Зареждане на етикетите от labels.json
with open(f"{MODEL_DIR}/labels.json", encoding="utf-8") as f:
    LABELS = json.load(f)

# Карти за дни от седмицата (на български, lower-case)
# Python's datetime.weekday(): 0=Monday through 6=Sunday
WEEKDAYS = {
    "понеделник": 0,
    "вторник": 1,
    "сряда": 2,
    "четвъртък": 3,
    "петък": 4,
    "събота": 5,
    "неделя": 6,
    # Handle variations
    "събота.": 5,
    "неделя.": 6,
    # Handle case variations
    "Понеделник": 0,
    "Вторник": 1,
    "Сряда": 2,
    "Четвъртък": 3,
    "Петък": 4,
    "Събота": 5,
    "Неделя": 6
}

# относителни думи
RELATIVE = {
    "днес": 0, "утре": 1, "вдругиден": 2
}

# подсказки за време от деня (ако няма изричен час)
DAYTIME_HINTS = {
    "сутринта": time(9, 0),
    "обед": time(12, 0),
    "наобед": time(12, 0),
    "следобед": time(15, 0),
    "вечерта": time(19, 0),
    "вечер": time(19, 0)
}

def _next_weekday(from_date: date, target_weekday: int) -> date:
    """Връща следващата дата за даден ден от седмицата (>= утре)."""
    # Convert datetime to date if needed
    current_date = from_date.date() if isinstance(from_date, datetime) else from_date
    
    # Get current weekday (0=Monday through 6=Sunday)
    current_weekday = current_date.weekday()
    
    # Calculate days until target
    days_ahead = target_weekday - current_weekday
    
    # If we have passed the target day this week or it's today,
    # we need to wait for next week
    if days_ahead <= 0:
        days_ahead += 7
    
    next_date = current_date + timedelta(days=days_ahead)
    
    # Verify we got the right weekday
    assert next_date.weekday() == target_weekday, f"Expected weekday {target_weekday}, got {next_date.weekday()}"
    
    return next_date

def _parse_day_from_tokens(day_tokens: list[str], now: datetime) -> Optional[date]:
    """Опитва да извлече дата (ден/дата) от токените с WHEN_DAY."""
    if not day_tokens:
        return None

    # Convert to lowercase and search in WEEKDAYS dictionary as is
    toks = day_tokens

    # 1) относителни думи (днес/утре/вдругиден)
    for t in toks:
        if t.lower() in RELATIVE:
            return (now + timedelta(days=RELATIVE[t.lower()])).date()

    # 2) ден от седмицата - search with original case first, then try lowercase
    for t in toks:
        weekday_val = WEEKDAYS.get(t)  # Try exact match first
        if weekday_val is None:
            weekday_val = WEEKDAYS.get(t.lower())  # Try lowercase as fallback
        if weekday_val is not None:
            return _next_weekday(now, weekday_val)

    # 3) дата от типа "20ти", "1ви", "2ри", "7ми", "20", "20."
    for t in toks:
        m = re.match(r"^(\d{1,2})(?:-?(ви|ри|ти|ми))?\.?$", t)
        if m:
            day = int(m.group(1))
            y, mth = now.year, now.month
            try:
                candidate = date(y, mth, day)
            except ValueError:
                if mth == 12:
                    candidate = date(y + 1, 1, day)
                else:
                    candidate = date(y, mth + 1, day)
            if candidate < now.date():
                if candidate.month == 12:
                    candidate = date(candidate.year + 1, 1, candidate.day)
                else:
                    for i in range(1, 3):
                        try:
                            candidate = date(y + (mth + i - 1) // 12,
                                             ((mth + i - 1) % 12) + 1,
                                             day)
                            break
                        except ValueError:
                            continue
            return candidate

    return None

def _parse_time_from_tokens(time_tokens: list[str]) -> Tuple[Optional[time], Optional[time]]:
    """Опитва да извлече начален и краен час от WHEN_START токени."""
    if not time_tokens:
        return None, None

    raw = " ".join(time_tokens).lower().strip()
    raw = raw.replace("ч.", "ч").replace("часа", "ч").replace(" часа", "ч").replace(" h", "ч")

    # Намираме всички числа във формат ЧЧ:ММ или ЧЧ
    times = []
    
    # Първо търсим формат ЧЧ:ММ
    for match in re.finditer(r"\b(\d{1,2})[:\.](\d{1,2})\b", raw):
        h = int(match.group(1))
        m = int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            times.append((time(h, m), match.start()))
    
    # После търсим формат ЧЧ
    for match in re.finditer(r"\b(\d{1,2})\s*ч?\b", raw):
        # Пропускаме, ако вече имаме число с минути на тази позиция
        skip = False
        for _, pos in times:
            if pos <= match.start() <= pos + len(match.group(0)):
                skip = True
                break
        if skip:
            continue
            
        h = int(match.group(1))
        if 0 <= h <= 23:
            times.append((time(h, 0), match.start()))
    
    # Сортираме по позиция в текста
    times.sort(key=lambda x: x[1])
    times = [t for t, _ in times]  # Премахваме позициите
    
    # Ако имаме две времена и второто е след думата "до", това е крайно време
    if len(times) == 2 and "до" in raw:
        return times[0], times[1]
    elif len(times) == 1:
        return times[0], None
    
    return None, None

def _find_daytime_hint(tokens: list[str], labels: list[str]) -> Optional[time]:
    """Ако няма WHEN_START, търсим думи като 'сутринта', 'следобед', 'вечерта' в WHEN_DAY токени."""
    for tok, lab in zip(tokens, labels):
        if lab in ("B-WHEN_DAY", "I-WHEN_DAY"):
            if tok.lower() in DAYTIME_HINTS:
                return DAYTIME_HINTS[tok.lower()]
    return None

def parse_text(text: str) -> dict:
    if not text or not text.strip():
        return {"title": "", "datetime": None, "tokens": [], "labels": [], "debug": {"model_dir": MODEL_DIR, "note": "empty text"}}

    words = text.split()
    encoding = tokenizer(words, is_split_into_words=True, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(input_ids=encoding["input_ids"], attention_mask=encoding["attention_mask"])
    logits = outputs.logits
    pred_ids = torch.argmax(logits, dim=-1).squeeze().tolist()

    word_ids = encoding.word_ids(batch_index=0)
    labels = []
    current = None
    
    # First pass - get model predictions
    for idx, wid in enumerate(word_ids):
        if wid is None:
            continue
        if wid != current:
            current = wid
            label_id = pred_ids[idx]
            labels.append(LABELS[label_id])
    
    # Second pass - fix weekday labels if model missed them
    fixed_labels = []
    for word, label in zip(words, labels):
        if label == "O" and word.lower() in WEEKDAYS:
            # If it's a weekday but was labeled as Other, fix it
            fixed_labels.append("B-WHEN_DAY")
        else:
            fixed_labels.append(label)
    
    labels = fixed_labels

    tokens = words
    
    # Намираме индексите на първия и последния значим токен
    first_index = -1
    last_index = -1
    for i, (token, label) in enumerate(zip(tokens, labels)):
        # Създаваме списък от думи, които са част от заглавието
        title_words = ["клас", "колелета", "тате", "офис", "мол"]  # добавете още думи при нужда
        
        if (label in ["B-TITLE", "B-PERSON", "B-PLACE"] or 
            token.lower() in title_words or 
            (i > 0 and tokens[i-1].lower() == "с" and token not in WEEKDAYS and not token.isdigit())):
            if first_index == -1:
                first_index = i
            last_index = i
    
    if first_index == -1:
        # Ако не сме намерили значими токени, вземаме само B-TITLE
        title_tokens = [t for t, lab in zip(tokens, labels) if lab == "B-TITLE"]
        title = " ".join(title_tokens).strip()
    else:
        # Вземаме всички токени между първия и последния значим токен
        title_tokens = tokens[first_index:last_index + 1]
        
        # Филтрираме само нежеланите свързващи думи и времеви маркери
        filtered_tokens = []
        for i, token in enumerate(title_tokens):
            # Проверяваме дали думата е времеви маркер или нежелана свързваща дума
            is_time_marker = token.lower() in ["сутринта", "вечерта", "следобед", "утре", "днес", "вдругиден"]
            is_weekday = token in WEEKDAYS or token.lower() in WEEKDAYS
            is_unwanted_connector = token.lower() in ["на", "от", "до"]
            
            if not is_time_marker and not is_weekday and not is_unwanted_connector:
                filtered_tokens.append(token)
        
        title = " ".join(filtered_tokens).strip()

    day_tokens = [t for t, lab in zip(tokens, labels) if lab in ("B-WHEN_DAY", "I-WHEN_DAY")]
    
    # Събираме всички времеви токени заедно със свързващите думи между тях
    time_section = []
    in_time_section = False
    for t, lab in zip(tokens, labels):
        if lab == "B-WHEN_START":
            in_time_section = True
            time_section.append(t)
        elif in_time_section and (lab == "O" or lab == "B-WHEN_START"):
            time_section.append(t)
        elif in_time_section:
            in_time_section = False
    
    start_tokens = time_section if time_section else []

    now = datetime.now()
    the_date = _parse_day_from_tokens(day_tokens, now)
    start_time, end_time = _parse_time_from_tokens(start_tokens) if start_tokens else (None, None)

    if start_time is None:
        start_time = _find_daytime_hint(tokens, labels)

    start_dt = None
    end_dt = None
    
    if the_date and start_time:
        start_dt = datetime.combine(the_date, start_time)
        if end_time:
            end_dt = datetime.combine(the_date, end_time)
            # If end time is earlier than start time, assume it's the next day
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
    elif the_date and not start_time:
        start_dt = None
    elif not the_date and start_time:
        tentative = datetime.combine(now.date(), start_time)
        if tentative < now:
            tentative += timedelta(days=1)
        start_dt = tentative
        if end_time:
            end_dt = datetime.combine(tentative.date(), end_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)

    if not title:
        non_when = [t for t, lab in zip(tokens, labels) if lab not in ("B-WHEN_DAY", "I-WHEN_DAY", "B-WHEN_START")]
        filtered = [t for t in non_when if t.lower() not in {"на", "в", "с", "от", "до"}]
        title = " ".join(filtered).strip()

    return {
        "title": title,
        "datetime": start_dt,  # For backward compatibility
        "start": start_dt,
        "end_datetime": end_dt,
        "tokens": tokens,
        "labels": labels,
        "debug": {"model_dir": MODEL_DIR, "note": "inference ok"}
    }

if __name__ == "__main__":
    tests = [
        "Онлайн лекция по програмиране в понеделник от 10 до 12",
        "тренировка с тате с колелета в събота в 9",
        "Тренировка с Тате с Колелета в събота в 9",
        "Йога клас утре сутринта",
        "Йога Клас утре сутринта",
        "Вечеря с гери в неделя от 18",
        "Вечеря с Гери в Неделя от 18"
    ]
    
    print("\nТестване на парсера:")
    print("-" * 80)
    for t in tests:
        res = parse_text(t)
        print("\nВход:", t)
        print("Заглавие:", res["title"])
        print("Токени:", ' | '.join(f"{t}[{l}]" for t, l in zip(res["tokens"], res["labels"])))
        start_tokens = [t for t, l in zip(res["tokens"], res["labels"]) if l == "B-WHEN_START"]
        print("Времеви токени:", start_tokens)
        if start_tokens:
            start, end = _parse_time_from_tokens(start_tokens)
            print("Разпознато време - начало:", start, "край:", end)
        print("Начало:", res["datetime"] or res["start"])
        print("Край:", res.get("end_datetime"))
        print("-" * 80)

    print("\nИнформация за модела:")
    print("Зареден от:", MODEL_DIR)
    print("Размер на речника:", tokenizer.vocab_size)
    print("Брой етикети:", model.config.num_labels)
    print("Налични етикети:", LABELS)