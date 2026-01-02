from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Try to load from .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Get DATABASE_URL - Vercel injects it directly, dotenv loads it locally
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to POSTGRES_URL if DATABASE_URL not set
if not DATABASE_URL:
    DATABASE_URL = os.getenv("POSTGRES_URL")

# Last resort: SQLite for local dev
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./events.db"

print(f"🗄️ Database URL: {DATABASE_URL[:30] if len(DATABASE_URL) > 30 else DATABASE_URL}...")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL - use connection pooling for serverless
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
    )

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()