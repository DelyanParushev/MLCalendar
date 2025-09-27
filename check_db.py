import sqlite3

try:
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables:', tables)
    
    # Check schema
    cursor.execute("PRAGMA table_info(events);")
    schema = cursor.fetchall()
    print('Schema:', schema)
    
    # Check record count
    cursor.execute("SELECT COUNT(*) FROM events;")
    count = cursor.fetchone()[0]
    print('Record count:', count)
    
    # Show sample records if any
    if count > 0:
        cursor.execute("SELECT * FROM events LIMIT 5;")
        records = cursor.fetchall()
        print('Sample records:', records)
    
    conn.close()
except Exception as e:
    print('Error:', e)