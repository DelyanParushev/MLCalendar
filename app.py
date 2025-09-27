from datetime import datetime, timedelta, time, date
from typing import Optional, Tuple
import os
import re
import json

import torch
from transformers import BertTokenizerFast, BertForTokenClassification
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Database setup
DATABASE_URL = "sqlite:///./events.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed only for SQLite
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Database Model
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=True)
    raw_text = Column(Text, nullable=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use the hosted model instead of local files
MODEL_NAME = "dex7er999/NLPCalendar"

# Зареждане на токенизатор и модел
tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)
model = BertForTokenClassification.from_pretrained(MODEL_NAME)
model.eval()

# Load labels from the model config
config = model.config
LABELS = [label for _, label in sorted(config.id2label.items(), key=lambda x: int(x[0]))]

# Use the same maps from nlp_parser_ml.py
WEEKDAYS = {
    "понеделник": 0, "вторник": 1, "сряда": 2, "четвъртък": 3, "петък": 4, "събота": 5, "неделя": 6,
    "събота.": 5, "неделя.": 6,
    "Понеделник": 0, "Вторник": 1, "Сряда": 2, "Четвъртък": 3, "Петък": 4, "Събота": 5, "Неделя": 6
}

RELATIVE = {"днес": 0, "утре": 1, "вдругиден": 2}

DAYTIME_HINTS = {
    "сутринта": time(9, 0), "обед": time(12, 0), "наобед": time(12, 0),
    "следобед": time(15, 0), "вечерта": time(19, 0), "вечер": time(19, 0)
}

def _next_weekday(from_date: date, target_weekday: int) -> date:
    current_date = from_date.date() if isinstance(from_date, datetime) else from_date
    current_weekday = current_date.weekday()
    days_ahead = target_weekday - current_weekday
    if days_ahead <= 0:
        days_ahead += 7
    next_date = current_date + timedelta(days=days_ahead)
    return next_date

def _parse_day_from_tokens(day_tokens: list[str], now: datetime) -> Optional[date]:
    if not day_tokens:
        return None

    for t in day_tokens:
        if t.lower() in RELATIVE:
            return (now + timedelta(days=RELATIVE[t.lower()])).date()

    for t in day_tokens:
        weekday_val = WEEKDAYS.get(t) or WEEKDAYS.get(t.lower())
        if weekday_val is not None:
            return _next_weekday(now, weekday_val)

    for t in day_tokens:
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
    if not time_tokens:
        return None, None

    raw = " ".join(time_tokens).lower().strip()
    raw = raw.replace("ч.", "ч").replace("часа", "ч").replace(" часа", "ч").replace(" h", "ч")

    times = []
    for match in re.finditer(r"\b(\d{1,2})[:\.](\d{1,2})\b", raw):
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            times.append((time(h, m), match.start()))

    for match in re.finditer(r"\b(\d{1,2})\s*ч?\b", raw):
        skip = any(pos <= match.start() <= pos + len(match.group(0)) for _, pos in times)
        if not skip:
            h = int(match.group(1))
            if 0 <= h <= 23:
                times.append((time(h, 0), match.start()))

    times.sort(key=lambda x: x[1])
    times = [t for t, _ in times]

    if len(times) == 2 and "до" in raw:
        return times[0], times[1]
    elif len(times) == 1:
        return times[0], None
    return None, None

def _find_daytime_hint(tokens: list[str], labels: list[str]) -> Optional[time]:
    for tok, lab in zip(tokens, labels):
        if lab in ("B-WHEN_DAY", "I-WHEN_DAY") and tok.lower() in DAYTIME_HINTS:
            return DAYTIME_HINTS[tok.lower()]
    return None

def parse_text(text: str) -> dict:
    if not text or not text.strip():
        return {
            "error": "не успях да разбера текста. Опитай да преформулираш.",
            "debug": {"model_name": MODEL_NAME, "note": "empty text"}
        }
    
    # Ensure proper UTF-8 encoding
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        elif isinstance(text, str):
            text = text.encode('utf-8').decode('utf-8')
    except Exception as e:
        print(f"Encoding error: {str(e)}")
        return {
            "error": "проблем с кодирането на текста",
            "debug": {"model_name": MODEL_NAME, "note": "encoding error"}
        }

    words = text.split()
    encoding = tokenizer(words, is_split_into_words=True, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(input_ids=encoding["input_ids"], attention_mask=encoding["attention_mask"])
    
    pred_ids = torch.argmax(outputs.logits, dim=-1).squeeze().tolist()
    word_ids = encoding.word_ids(batch_index=0)
    
    labels = []
    current = None
    for idx, wid in enumerate(word_ids):
        if wid is not None and wid != current:
            current = wid
            labels.append(LABELS[pred_ids[idx]])

    fixed_labels = [
        "B-WHEN_DAY" if label == "O" and word.lower() in WEEKDAYS else label
        for word, label in zip(words, labels)
    ]
    labels = fixed_labels
    tokens = words

    # Extract title
    first_index = -1
    last_index = -1
    title_words = {"клас", "колелета", "тате", "офис", "мол"}
    
    for i, (token, label) in enumerate(zip(tokens, labels)):
        if (label in ["B-TITLE", "B-PERSON", "B-PLACE"] or 
            token.lower() in title_words or 
            (i > 0 and tokens[i-1].lower() == "с" and token not in WEEKDAYS and not token.isdigit())):
            if first_index == -1:
                first_index = i
            last_index = i

    if first_index == -1:
        title_tokens = [t for t, lab in zip(tokens, labels) if lab == "B-TITLE"]
        title = " ".join(title_tokens).strip()
    else:
        title_tokens = tokens[first_index:last_index + 1]
        filtered_tokens = []
        
        for token in title_tokens:
            if not (
                token.lower() in {"сутринта", "вечерта", "следобед", "утре", "днес", "вдругиден"} or
                token in WEEKDAYS or token.lower() in WEEKDAYS or
                token.lower() in {"на", "от", "до"}
            ):
                filtered_tokens.append(token)
        
        title = " ".join(filtered_tokens).strip()

    day_tokens = [t for t, lab in zip(tokens, labels) if lab in ("B-WHEN_DAY", "I-WHEN_DAY")]
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

    if not title or not start_dt:
        return {
            "error": "не успях да разбера текста. Опитай да преформулираш.",
            "debug": {
                "tokens": tokens,
                "labels": labels,
                "model_name": MODEL_NAME,
                "note": "missing title or datetime"
            }
        }

    return {
        "title": title,
        "datetime": start_dt,  # For backward compatibility
        "start": start_dt,
        "end_datetime": end_dt,
        "tokens": tokens,
        "labels": labels,
        "debug": {"model_name": MODEL_NAME, "note": "inference ok"}
    }

app = FastAPI(title="AI Calendar API", version="0.1.0")

# Create an API router with /api prefix
api_router = FastAPI(title="AI Calendar API", version="0.1.0")

# Add CORS middleware to the API router
api_router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add this to handle JSON encoding properly
@api_router.middleware("http")
async def add_charset_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

# Mount the API router under /api prefix
app.mount("/api", api_router)

@api_router.get("/")
def read_root():
    return {
        "status": "ok",
        "model_name": MODEL_NAME,
        "labels": LABELS
    }

@api_router.post("/parse")
def parse_event(payload: dict):
    text = payload.get("text", "")
    if not text:
        return {"error": "Не е подаден текст."}

    result = parse_text(text)
    if "error" in result:
        return result

    dt = result.get("datetime") or result.get("start")  # Backwards compatibility
    end = result.get("end_datetime")
    if not end and dt:
        end = dt + timedelta(hours=1)
        
    return {
        "title": result.get("title", ""),
        "start": dt.isoformat(),
        "end": end.isoformat() if end else None,
        "tokens": result.get("tokens", []),
        "labels": result.get("labels", []),
        "debug": result.get("debug", {})
    }

@api_router.get("/events")
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return [
        {
            "id": event.id,
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
            "raw_text": event.raw_text
        }
        for event in events
    ]

@api_router.post("/events")
def create_event(payload: dict, db: Session = Depends(get_db)):
    print(f"Received payload: {payload}")  # Debug log
    
    try:
        if all(key in payload for key in ["title", "start"]):
            # Direct event data
            title = payload["title"]
            start = datetime.fromisoformat(payload["start"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(payload["end"].replace("Z", "+00:00")) if payload.get("end") else start + timedelta(hours=1)
            raw_text = payload.get("raw_text", "")
        else:
            # Parse from text
            text = payload.get("text", "")
            if not text:
                return {"error": "Не е подаден текст."}
                
            result = parse_text(text)
            if "error" in result:
                return result

            title = result["title"]
            start = result.get("datetime") or result["start"]
            end = result.get("end_datetime") or (start + timedelta(hours=1))
            raw_text = text

        event = Event(
            title=title,
            start=start,
            end=end,
            raw_text=raw_text
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return {
            "id": event.id,
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None
        }
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        db.rollback()
        return {"error": "Internal server error", "detail": str(e)}

@api_router.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {"error": "Event not found"}
            
        db.delete(event)
        db.commit()
        return {"message": "Event deleted successfully"}
    except Exception as e:
        print(f"Error deleting event: {str(e)}")
        db.rollback()
        return {"error": "Internal server error", "detail": str(e)}
