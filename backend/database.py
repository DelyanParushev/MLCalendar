from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Get DATABASE_URL from environment
# Vercel injects this directly, no dotenv needed
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Try alternative names that Vercel might use
    DATABASE_URL = os.environ.get("POSTGRES_URL")
    
if not DATABASE_URL:
    # Local development fallback
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./events.db")

print(f"🗄️ Database URL: {DATABASE_URL[:30] if DATABASE_URL else 'NOT SET'}...")

# Configure engine based on database type
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # only for SQLite
    )
elif DATABASE_URL:
    # PostgreSQL or other databases
    # Add pool settings for serverless
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=300,    # Recycle connections after 5 minutes
    )
else:
    # No database configured - create a dummy engine
    raise RuntimeError("❌ No DATABASE_URL configured! Please set it in Vercel environment variables.")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()