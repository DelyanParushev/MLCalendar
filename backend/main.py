# backend/main.py
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from . import models, schemas, auth, google_oauth
from ml.nlp_parser_ml import parse_text
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Calendar API", version="0.2.0")

# CORS configuration from environment
cors_origins = os.getenv("CORS_ORIGINS", "https://ml-calendar.vercel.app,http://localhost:5173,http://localhost:3000")
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
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Database initialization with error handling
@app.on_event("startup")
async def startup_event():
    try:
        print("🚀 Starting application...")
        print(f"🌐 Environment: {os.getenv('VERCEL_ENV', 'local')}")
        print(f"🌐 CORS Origins: {cors_origins_list}")
        
        database_url = os.getenv("DATABASE_URL", "")
        print(f"🗄️ DATABASE_URL: {database_url[:30]}...")
        
        # Skip database operations for SQLite in serverless
        if database_url.startswith("sqlite"):
            print("⚠️ SQLite detected in serverless - skipping table creation")
            return
        
        if not database_url:
            print("⚠️ No DATABASE_URL set - tables may not persist")
            return
        
        # Create all tables for PostgreSQL/Neon
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
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
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires  # Use email as subject
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/google", response_model=schemas.Token)
def google_login(payload: dict, db: Session = Depends(get_db)):
    """
    Authenticate user with Google ID token
    Expects: { "token": "google_id_token" }
    """
    google_token = payload.get("token")
    if not google_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token not provided"
        )
    
    # Verify the Google token
    google_user_info = google_oauth.verify_google_token(google_token)
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    if not google_user_info.get('email_verified'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google email not verified"
        )
    
    # Get or create user
    user = google_oauth.get_or_create_google_user(db, google_user_info)
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

# Event parsing endpoint (no auth required for parsing)
@app.post("/parse")
def parse_event(payload: dict):
    try:
        text = payload.get("text", "")
        if not text:
            return {"error": "Не е подаден текст."}

        print(f"🔍 Parsing request: '{text}'")
        result = parse_text(text)
        print(f"🔍 Parse result: {result}")
        
        dt = result.get("datetime") or result.get("start")  # Backwards compatibility
        print(f"📅 Parsed datetime object: {dt} (type: {type(dt)})")
        
        if dt is None:
            return {
                "error": "Не можах да разбера датата/часа.",
                "debug": {
                    "tokens": result.get("tokens", []),
                    "labels": result.get("labels", []),
                    **(result.get("debug") or {})
                }
            }

        # Convert string datetime to datetime object if needed
        if isinstance(dt, str):
            try:
                # Handle various datetime string formats
                if dt.endswith('Z'):
                    dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                elif '+' in dt or dt.endswith(('00:00', '+0000')):
                    dt = datetime.fromisoformat(dt)
                else:
                    # Naive datetime string - parse without timezone
                    dt = datetime.fromisoformat(dt)
                print(f"🔍 Converted datetime: {dt}")
            except ValueError as e:
                print(f"❌ DateTime conversion error: {e}")
                return {
                    "error": "Невалиден формат на датата.",
                    "debug": {"raw_datetime": dt, "conversion_error": str(e)}
                }

        end = result.get("end_datetime") or result.get("end")  # Get the end time from parse_text
        
        # Convert string end datetime to datetime object if needed
        if isinstance(end, str):
            try:
                # Handle various datetime string formats
                if end.endswith('Z'):
                    end = datetime.fromisoformat(end.replace('Z', '+00:00'))
                elif '+' in end or end.endswith(('00:00', '+0000')):
                    end = datetime.fromisoformat(end)
                else:
                    # Naive datetime string - parse without timezone
                    end = datetime.fromisoformat(end)
                print(f"🔍 Converted end datetime: {end}")
            except ValueError:
                print("⚠️ Could not convert end datetime, will calculate from start")
                end = None
        
        # If no end time is specified, set it to start time + 1 hour
        if not end and dt:
            end = dt + timedelta(hours=1)
            print(f"🔍 Calculated end time: {end}")
    
    except Exception as e:
        print(f"❌ Parse endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": "Вътрешна грешка при парсиране.",
            "debug": {"exception": str(e)}
        }
    
    # Generate ISO format strings
    start_iso = dt.isoformat()
    end_iso = end.isoformat() if end else None
    
    print(f"📤 Returning to frontend - Start ISO: {start_iso}, End ISO: {end_iso}")
        
    return {
        "title": result.get("title", ""),
        "start": start_iso,
        "end": end_iso,
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
    print(f"🔍 Creating event with payload: {payload}")
    
    # Check if we have pre-parsed data
    if "title" in payload and "start" in payload:
        # Use pre-parsed data from frontend
        # Parse the datetime and ensure it's timezone-aware
        start_str = payload["start"]
        print(f"📅 Original start string: {start_str}")
        
        if start_str.endswith('Z'):
            # Handle UTC format
            start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        elif '+' in start_str or start_str.endswith(('00:00', '+0000')):
            # Already has timezone info
            start = datetime.fromisoformat(start_str)
        else:
            # No timezone info - assume it's the user's local time
            # Parse as naive datetime and don't add timezone info
            start = datetime.fromisoformat(start_str)
            print(f"🕐 Parsed start time (naive): {start}")
        
        # Handle end time similarly
        if payload.get("end"):
            end_str = payload["end"]
            print(f"📅 Original end string: {end_str}")
            
            if end_str.endswith('Z'):
                end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            elif '+' in end_str or end_str.endswith(('00:00', '+0000')):
                end = datetime.fromisoformat(end_str)
            else:
                end = datetime.fromisoformat(end_str)
                print(f"🕐 Parsed end time (naive): {end}")
        else:
            # If no end time, set it to start time + 1 hour
            end = start + timedelta(hours=1)
            print(f"🕐 Calculated end time: {end}")
        
        obj = models.Event(
            title=payload["title"],
            start=start,
            end=end,
            raw_text=payload.get("raw_text"),
            owner_id=current_user.id
        )
        
        print(f"💾 Saving event - Title: {obj.title}, Start: {obj.start}, End: {obj.end}")
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
