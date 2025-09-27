# backend/main.py
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from . import models, schemas, auth
from ml.nlp_parser_ml import parse_text
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Calendar API", version="0.2.0")

# CORS configuration from environment
cors_origins = os.getenv("CORS_ORIGINS", "https://ml-calendar.vercel.app,http://localhost:5173")
if cors_origins == "*":
    cors_origins_list = ["*"]
else:
    cors_origins_list = [origin.strip() for origin in cors_origins.split(",")]

print(f"🌐 CORS Origins: {cors_origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Database initialization with error handling
@app.on_event("startup")
async def startup_event():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # For PostgreSQL, run initial setup
        database_url = os.getenv("DATABASE_URL", "")
        if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
            print("🐘 PostgreSQL detected - running initial setup...")
            
            # Create admin user if not exists
            session = SessionLocal()
            try:
                admin_user = session.query(models.User).filter_by(username="admin").first()
                if not admin_user:
                    print("👤 Creating default admin user...")
                    admin_user = models.User(
                        email="admin@example.com",
                        username="admin",
                        hashed_password=auth.get_password_hash("admin"),
                        created_at=datetime.utcnow(),
                        is_active=True
                    )
                    session.add(admin_user)
                    session.commit()
                    print("✅ Admin user created successfully!")
            except Exception as e:
                session.rollback()
                print(f"⚠️ Error creating admin user: {e}")
            finally:
                session.close()
        
        print("✅ Database initialization completed!")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        # Don't crash the app, let it start anyway

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "AI Calendar API is running!",
        "version": "0.2.0",
        "cors_origins": os.getenv("CORS_ORIGINS", "not-set")
    }

@app.get("/health")
def health_check_detailed():
    return {
        "status": "healthy",
        "database": "connected",
        "cors_origins": os.getenv("CORS_ORIGINS", "not-set"),
        "ml_model": os.getenv("ENABLE_ML_MODEL", "false")
    }

# Authentication endpoints
@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    db_user = auth.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

# Event parsing endpoint (no auth required for parsing)
@app.post("/parse")
def parse_event(payload: dict):
    text = payload.get("text", "")
    if not text:
        return {"error": "Не е подаден текст."}

    result = parse_text(text)
    dt = result.get("datetime") or result.get("start")  # Backwards compatibility
    if dt is None:
        return {
            "error": "Не можах да разбера датата/часа.",
            "debug": {
                "tokens": result.get("tokens", []),
                "labels": result.get("labels", []),
                **(result.get("debug") or {})
            }
        }

    end = result.get("end_datetime")  # Get the end time from parse_text
    # If no end time is specified, set it to start time + 1 hour
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

# Protected event endpoints
@app.post("/events", response_model=schemas.EventOut)
def create_event(
    payload: dict, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Check if we have pre-parsed data
    if "title" in payload and "start" in payload:
        # Use pre-parsed data from frontend
        start = datetime.fromisoformat(payload["start"])
        # If end time is not specified, set it to start time + 1 hour
        end = datetime.fromisoformat(payload["end"]) if payload.get("end") else (start + timedelta(hours=1))
        
        obj = models.Event(
            title=payload["title"],
            start=start,
            end=end,
            raw_text=payload.get("raw_text"),
            owner_id=current_user.id
        )
    else:
        # Parse from raw text
        text = payload.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Не е подаден текст.")

        result = parse_text(text)
        title = result.get("title", "")
        dt = result.get("datetime") or result.get("start")  # Backwards compatibility
        if dt is None:
            raise HTTPException(status_code=400, detail="Не можах да разбера датата/часа.")
            
        end = result.get("end_datetime")
        if not end:
            end = dt + timedelta(hours=1)

        obj = models.Event(
            title=title, 
            start=dt, 
            end=end, 
            raw_text=text,
            owner_id=current_user.id
        )

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.get("/events", response_model=list[schemas.EventOut])
def list_events(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return db.query(models.Event).filter(
        models.Event.owner_id == current_user.id
    ).order_by(models.Event.start.asc()).all()

@app.delete("/events/{event_id}", response_model=schemas.EventOut)
def delete_event(
    event_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.owner_id == current_user.id
    ).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Събитието не е намерено")
    db.delete(event)
    db.commit()
    return event
