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
            conn.execute(text("SELECT password_hash FROM users LIMIT 1"))
            print("   ✅ 'password_hash' column already exists.")
        except Exception:
            print("   ❌ 'password_hash' missing. Fixing...")
            conn.rollback()
            try:
                conn.execute(text("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash"))
                print("   ✅ Renamed 'hashed_password' to 'password_hash'")
            except Exception:
                conn.rollback()
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
                    print("   ✅ Created new 'password_hash' column")
                except Exception as e:
                    print(f"   🔥 Failed to fix users table: {e}")

        # --- FIX 2: ARENA TABLE ---
        print("\n2️⃣ Checking 'arena_session_questions' table...")
        try:
            conn.execute(text("SELECT question_meta FROM arena_session_questions LIMIT 1"))
            print("   ✅ 'question_meta' column already exists.")
        except Exception:
            conn.rollback() 
            # If table doesn't exist, ignore. If column missing, try fix.
            try:
                # check if table exists first
                conn.execute(text("SELECT 1 FROM arena_session_questions LIMIT 1"))
                print("   ❌ 'question_meta' missing. Fixing...")
                try:
                    conn.execute(text("ALTER TABLE arena_session_questions RENAME COLUMN metadata TO question_meta"))
                    print("   ✅ Renamed 'metadata' to 'question_meta'")
                except Exception:
                    conn.rollback()
                    conn.execute(text("ALTER TABLE arena_session_questions ADD COLUMN question_meta JSON"))
                    print("   ✅ Created 'question_meta' column")
            except Exception:
                print("   ⚠️ Arena table likely doesn't exist yet (Skipping).")
                conn.rollback()

        # --- FIX 3: STUDY SETS TABLE (The Critical Fix) ---
        print("\n3️⃣ Checking 'study_sets' table for time tracking...")
        try:
            conn.execute(text("SELECT total_time_studied FROM study_sets LIMIT 1"))
            print("   ✅ 'total_time_studied' column already exists.")
        except Exception:
            print("   ❌ 'total_time_studied' missing. Attempting repair...")
            conn.rollback()
            
            # Check if the 'ms' version exists and rename it
            renamed = False
            try:
                conn.execute(text("SELECT total_time_studied_ms FROM study_sets LIMIT 1"))
                conn.execute(text("ALTER TABLE study_sets RENAME COLUMN total_time_studied_ms TO total_time_studied"))
                print("   ✅ Renamed 'total_time_studied_ms' to 'total_time_studied'")
                renamed = True
            except Exception:
                conn.rollback()

            # If rename didn't happen, create the column
            if not renamed:
                try:
                    conn.execute(text("ALTER TABLE study_sets ADD COLUMN total_time_studied INTEGER DEFAULT 0"))
                    print("   ✅ Created 'total_time_studied' column")
                except Exception as e:
                    print(f"   🔥 Failed to add column: {e}")

        conn.commit()
        print("\n✨ Schema Repair Complete!")

if __name__ == "__main__":
    fix_schema()