import sys
import os

# Ensure we can import from the app folder
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.database import engine

def fix_schema():
    print("🔧 Starting Schema Repair...")
    with engine.connect() as conn:
        # --- FIX 1: USERS TABLE ---
        print("\n1️⃣ Checking 'users' table...")
        try:
            # Check if correct column exists
            conn.execute(text("SELECT password_hash FROM users LIMIT 1"))
            print("   ✅ 'password_hash' column already exists.")
        except Exception:
            print("   ❌ 'password_hash' missing. Attempting to rename...")
            # Rollback the failed transaction so we can try fixing
            conn.rollback()
            
            fixed = False
            # Try renaming 'hashed_password' -> 'password_hash'
            try:
                conn.execute(text("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash"))
                print("   ✅ Renamed 'hashed_password' to 'password_hash'")
                fixed = True
            except Exception:
                conn.rollback()

            if not fixed:
                # Try renaming 'password' -> 'password_hash'
                try:
                    conn.execute(text("ALTER TABLE users RENAME COLUMN password TO password_hash"))
                    print("   ✅ Renamed 'password' to 'password_hash'")
                    fixed = True
                except Exception:
                    conn.rollback()
            
            if not fixed:
                # If neither exists, create it (worst case)
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
                    print("   ✅ Created new 'password_hash' column")
                except Exception as e:
                    print(f"   🔥 Failed to fix users table: {e}")

        # --- FIX 2: ARENA QUESTIONS TABLE ---
        print("\n2️⃣ Checking 'arena_session_questions' table...")
        try:
            # Check if table exists first
            conn.execute(text("SELECT 1 FROM arena_session_questions LIMIT 1"))
            
            # Check if correct column exists
            try:
                conn.execute(text("SELECT question_meta FROM arena_session_questions LIMIT 1"))
                print("   ✅ 'question_meta' column already exists.")
            except Exception:
                print("   ❌ 'question_meta' missing. Fixing renamed column...")
                conn.rollback()
                
                try:
                    conn.execute(text("ALTER TABLE arena_session_questions RENAME COLUMN metadata TO question_meta"))
                    print("   ✅ Renamed 'metadata' to 'question_meta'")
                except Exception:
                    conn.rollback()
                    try:
                        conn.execute(text("ALTER TABLE arena_session_questions ADD COLUMN question_meta JSON"))
                        print("   ✅ Created 'question_meta' column")
                    except Exception as e:
                        print(f"   🔥 Could not fix arena table: {e}")

        except Exception:
            print("   ⚠️ Table 'arena_session_questions' does not exist yet (Safe to ignore if not generated).")
            conn.rollback()

        conn.commit()
        print("\n✨ Schema Repair Complete!")

if __name__ == "__main__":
    fix_schema()