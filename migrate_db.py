#!/usr/bin/env python3
"""
Database migration script to add User table and update Event table.
Run this script to migrate from the old schema to the new one.
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.database import DATABASE_URL
from backend.models import Base, User, Event
from backend.auth import get_password_hash

def migrate_database():
    print("Starting database migration...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    
    # Check current schema
    with engine.connect() as conn:
        # Check if users table exists
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users';"))
        users_table_exists = result.fetchone() is not None
        
        # Check if events table has owner_id column
        result = conn.execute(text("PRAGMA table_info(events);"))
        columns = [row[1] for row in result.fetchall()]
        owner_id_exists = 'owner_id' in columns
        
        print(f"Users table exists: {users_table_exists}")
        print(f"Events table has owner_id: {owner_id_exists}")
    
    session = SessionLocal()
    
    try:
        # Create users table if it doesn't exist
        if not users_table_exists:
            print("Creating users table...")
            User.__table__.create(bind=engine)
            
            # Create default admin user
            print("Creating default admin user...")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin"),
                created_at=datetime.utcnow(),
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
        else:
            # Get existing admin user
            admin_user = session.query(User).filter_by(username="admin").first()
            if not admin_user:
                print("Creating admin user...")
                admin_user = User(
                    email="admin@example.com",
                    username="admin",
                    hashed_password=get_password_hash("admin"),
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                session.add(admin_user)
                session.commit()
                session.refresh(admin_user)
        
        # Handle events table migration
        if not owner_id_exists:
            print("Adding owner_id to events table...")
            
            # For SQLite, we need to recreate the table to add the foreign key
            with engine.connect() as conn:
                # Rename existing table
                conn.execute(text("ALTER TABLE events RENAME TO events_old;"))
                
                # Create new events table with proper schema
                Event.__table__.create(bind=engine)
                
                # Copy data from old table to new table
                conn.execute(text("""
                    INSERT INTO events (id, title, start, end, raw_text, owner_id)
                    SELECT id, title, start, end, raw_text, :admin_id FROM events_old;
                """), {"admin_id": admin_user.id})
                
                # Count migrated events
                result = conn.execute(text("SELECT COUNT(*) FROM events;"))
                event_count = result.scalar()
                
                # Drop old table
                conn.execute(text("DROP TABLE events_old;"))
                conn.commit()
                
                print(f"✅ Migrated {event_count} events to belong to admin user.")
        
        print("✅ Migration completed successfully!")
        print("Default admin credentials:")
        print("  Username: admin")
        print("  Password: admin")
        print("  Email: admin@example.com")
        print("\n⚠️  Please change the admin password after first login!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_database()