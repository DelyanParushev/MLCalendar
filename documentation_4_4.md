# 4.4 Конфигурация и работа с базата данни

Този раздел описва реализацията на базата данни в проекта, включващи конфигурация на SQLAlchemy, дефиниране на модели и CRUD операции за управление на календарни събития.

## 4.4.1 Използване на SQLAlchemy и SQLite

### Конфигурация на базата данни (database.py)

Конфигурацията на базата данни се намира в файла `backend/database.py` и осигурява основните компоненти за работа с SQLite база данни чрез SQLAlchemy ORM.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./events.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # само за SQLite в single-thread dev
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
```

**Ключови компоненти:**

1. **DATABASE_URL**: Дефинира SQLite файла `events.db` като основна база данни
2. **Engine**: Създава връзка с базата данни със специфична конфигурация за SQLite
3. **SessionLocal**: Factory функция за създаване на нови сесии с база данни
4. **Base**: Декларативна база класа от която наследяват всички модели

**Конфигурационни особености:**
- `check_same_thread=False` - необходим за SQLite в многонишкови приложения
- `autocommit=False` - осигурява експлицитно управление на транзакциите
- `autoflush=False` - предотвратява автоматично синхронизиране преди заявки

### Дефиниране на модели (models.py)

Моделът `Event` представлява основната структура за съхранение на календарни събития:

```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from .database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=True)
    raw_text = Column(Text, nullable=True)
```

**Структура на таблицата:**
- `id`: Първичен ключ, автоматично генерирано уникално ID
- `title`: Заглавие на събитието (до 255 символа, задължително)
- `start`: Начална дата и час със часова зона (задължително)
- `end`: Крайна дата и час със часова зона (незадължително)
- `raw_text`: Оригинален текст въведен от потребителя (незадължително)

### Схеми за валидация (schemas.py)

Pydantic схемите осигуряват валидация и сериализация на данните:

```python
class EventCreate(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    raw_text: Optional[str] = None

class EventOut(BaseModel):
    id: int
    title: str
    start: datetime
    end: Optional[datetime] = None
    raw_text: Optional[str] = None

    model_config = {"from_attributes": True}
```

## 4.4.2 CRUD операции и връзка с API

### Dependency Injection

Системата използва FastAPI dependency injection за управление на сесиите:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### CREATE операция

Създаването на нови събития се реализира чрез POST заявка към `/events`:

```python
@app.post("/events", response_model=schemas.EventOut)
def create_event(payload: dict, db: Session = Depends(get_db)):
    # Проверка за предварително парсирани данни
    if "title" in payload and "start" in payload:
        start = datetime.fromisoformat(payload["start"])
        end = datetime.fromisoformat(payload["end"]) if payload.get("end") else (start + timedelta(hours=1))
        
        obj = models.Event(
            title=payload["title"],
            start=start,
            end=end,
            raw_text=payload.get("raw_text")
        )
    else:
        # Парсиране от raw текст
        text = payload.get("text", "")
        result = parse_text(text)
        title = result.get("title", "")
        dt = result.get("datetime") or result.get("start")
        end = result.get("end_datetime") or (dt + timedelta(hours=1))

        obj = models.Event(title=title, start=dt, end=end, raw_text=text)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
```

**Особености:**
- Поддържа два начина на създаване: чрез предварително парсирани данни или raw текст
- Автоматично добавя 1 час към началото, ако крайното време не е зададено
- Използва ML модел за парсиране на естествен език

### READ операция

Извличането на събития се реализира чрез GET заявка към `/events`:

```python
@app.get("/events", response_model=list[schemas.EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).order_by(models.Event.start.asc()).all()
```

**Характеристики:**
- Връща всички събития сортирани по начална дата
- Автоматична сериализация чрез Pydantic схеми

### DELETE операция

Изтриването на събития се реализира чрез DELETE заявка към `/events/{event_id}`:

```python
@app.delete("/events/{event_id}", response_model=schemas.EventOut)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Събитието не е намерено")
    db.delete(event)
    db.commit()
    return event
```

**Функционалности:**
- Проверка за съществуване на събитието
- HTTP 404 грешка при несъществуващо ID
- Връща изтритото събитие като потвърждение

### Инициализация на базата данни

При стартиране на приложението, базата данни се инициализира автоматично:

```python
# DB init
Base.metadata.create_all(bind=engine)
```

Този код създава всички таблици автоматично при първо стартиране.

## ER Диаграма на базата данни

```
┌─────────────────────────────────┐
│             events              │
├─────────────────────────────────┤
│ id (PK)         │ INTEGER       │
│ title           │ VARCHAR(255)  │ NOT NULL
│ start           │ DATETIME      │ NOT NULL (timezone=True)
│ end             │ DATETIME      │ NULL (timezone=True)
│ raw_text        │ TEXT          │ NULL
└─────────────────────────────────┘
```

**Връзки и ограничения:**
- `id` е първичен ключ (Primary Key) с автоматично генериране
- `title` и `start` са задължителни полета
- `end` и `raw_text` са незадължителни
- Всички datetime полета поддържат часови зони

## Статистики от базата данни

На базата на текущото състояние на базата данни:
- **Брой таблици**: 1 (events)
- **Брой записи**: 36 събития
- **Примерни записи**:
  - Вечеря с Гери в Неделя от 18:00
  - Йога клас утре сутринта в 09:00
  - Разходка в различни дни от 21:00

Това показва, че системата активно се използва и успешно съхранява календарни събития с различни типове активности.

## Заключение

Реализацията на базата данни осигурява:
- Ефективно съхранение на календарни събития
- Автоматична валидация на данни
- Гъвкава архитектура чрез SQLAlchemy ORM
- Интеграция с ML модул за обработка на естествен език
- Пълна поддръжка на CRUD операции чрез REST API