#!/usr/bin/env python3
"""
Simple database migration script using direct SQL
"""
import sqlite3
import os
from datetime import datetime
from backend.auth import get_password_hash

def migrate_database():
    db_path = "events.db"
    
    if not os.path.exists(db_path):
        print("❌ Database doesn't exist!")
        return False
    
    print("Starting database migration...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(events);")
        columns = [row[1] for row in cursor.fetchall()]
        owner_id_exists = 'owner_id' in columns
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        users_table_exists = cursor.fetchone() is not None
        
        print(f"Users table exists: {users_table_exists}")
        print(f"Events table has owner_id: {owner_id_exists}")
        
        # Create users table if needed
        if not users_table_exists:
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER NOT NULL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX ix_users_id ON users (id);")
            cursor.execute("CREATE INDEX ix_users_email ON users (email);")
            cursor.execute("CREATE INDEX ix_users_username ON users (username);")
        
        # Create admin user if needed
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin';")
        admin_exists = cursor.fetchone()[0] > 0
        
        if not admin_exists:
            print("Creating admin user...")
            hashed_password = get_password_hash("admin")
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, is_active, created_at)
                VALUES (?, ?, ?, ?, ?);
            """, ("admin@example.com", "admin", hashed_password, True, created_at))
        
        # Get admin user ID
        cursor.execute("SELECT id FROM users WHERE username = 'admin';")
        admin_id = cursor.fetchone()[0]
        
        # Migrate events table if needed
        if not owner_id_exists:
            print("Migrating events table...")
            
            # Get current events
            cursor.execute("SELECT id, title, start, end, raw_text FROM events;")
            events = cursor.fetchall()
            
            # Drop and recreate events table
            cursor.execute("DROP TABLE events;")
            cursor.execute("""
                CREATE TABLE events (
                    id INTEGER NOT NULL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    start DATETIME NOT NULL,
                    end DATETIME,
                    raw_text TEXT,
                    owner_id INTEGER NOT NULL,
                    FOREIGN KEY(owner_id) REFERENCES users (id)
                );
            """)
            cursor.execute("CREATE INDEX ix_events_id ON events (id);")
            
            # Insert events back with owner_id
            for event in events:
                cursor.execute("""
                    INSERT INTO events (id, title, start, end, raw_text, owner_id)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (*event, admin_id))
            
            print(f"✅ Migrated {len(events)} events to belong to admin user.")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("Default admin credentials:")
        print("  Username: admin")
        print("  Password: admin")
        print("  Email: admin@example.com")
        print("\n⚠️  Please change the admin password after first login!")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration error: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    exit(0 if success else 1)