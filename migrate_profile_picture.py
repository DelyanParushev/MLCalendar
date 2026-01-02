"""
Database migration script to add profile_picture column to users table
Run this once to update your existing database
"""
import sqlite3
import os

# Path to your database
DATABASE_PATH = "events.db"

def migrate():
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database not found at {DATABASE_PATH}")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'profile_picture' in columns:
            print("✅ Column 'profile_picture' already exists in users table")
        else:
            # Add the new column
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500)")
            conn.commit()
            print("✅ Successfully added 'profile_picture' column to users table")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate()
    print("✅ Migration complete!")
