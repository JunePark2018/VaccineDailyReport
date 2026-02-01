import sqlite3
import os

def migrate_drop_column():
    # Determine DB path
    db_path = os.path.join("backend", "sql.db")
    
    if not os.path.exists(db_path):
        if os.path.exists("sql.db"):
             db_path = "sql.db"
        else:
            print(f"Database not found at {db_path} or ./sql.db")
            return

    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        if "marketing_agree" in columns:
            print("Dropping column 'marketing_agree'...")
            # SQLite >= 3.35.0 supports DROP COLUMN
            cursor.execute("ALTER TABLE users DROP COLUMN marketing_agree")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column 'marketing_agree' not found. It might have been already deleted.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        # Fallback for old SQLite if needed (Create new table, copy, rename)
        if "syntax error" in str(e) or "near \"DROP\": syntax error" in str(e):
             print("SQLite version might be old. Trying manual table recreation method is recommended if this fails.")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_drop_column()
