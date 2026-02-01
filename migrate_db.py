import sqlite3
import os

def migrate():
    # Determine DB path
    db_path = os.path.join("backend", "sql.db")
    
    if not os.path.exists(db_path):
        # Try absolute path or current dir check
        if os.path.exists("sql.db"):
             db_path = "sql.db"
        else:
            print(f"Database not found at {db_path} or ./sql.db")
            print(f"Current CWD: {os.getcwd()}")
            return

    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Table 'users' does not exist.")
            return

        # Check columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        if "user_real_name" in columns:
            print("Renaming user_real_name to username...")
            cursor.execute("ALTER TABLE users RENAME COLUMN user_real_name TO username")
            conn.commit()
            print("Migration successful.")
        elif "username" in columns:
            print("Column 'username' already exists. No migration needed.")
        else:
            print("Neither 'user_real_name' nor 'username' column found.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
