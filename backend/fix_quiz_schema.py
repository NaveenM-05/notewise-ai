import sys
import os
from sqlalchemy import text

# Ensure we can import from the app folder
sys.path.append(os.getcwd())

try:
    from app.database import engine
except ImportError:
    # Fallback if run from inside app folder
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from app.database import engine

def fix_quiz_table():
    print("🔧 Fixing 'quiz_sessions' table...")
    with engine.connect() as conn:
        
        # 1. Fix 'score' column
        try:
            conn.execute(text("ALTER TABLE quiz_sessions ADD COLUMN score INTEGER DEFAULT 0"))
            print("   ✅ SUCCESS: Created 'score' column.")
        except Exception as e:
            print(f"   ℹ️ 'score' column check: {e}")
            conn.rollback()

        # 2. Fix 'answers' column (to store the JSON)
        try:
            conn.execute(text("ALTER TABLE quiz_sessions ADD COLUMN answers JSON"))
            print("   ✅ SUCCESS: Created 'answers' column.")
        except Exception as e:
            print(f"   ℹ️ 'answers' column check: {e}")
            conn.rollback()

        # 3. Fix 'duration_ms' column
        try:
            conn.execute(text("ALTER TABLE quiz_sessions ADD COLUMN duration_ms INTEGER DEFAULT 0"))
            print("   ✅ SUCCESS: Created 'duration_ms' column.")
        except Exception as e:
            print(f"   ℹ️ 'duration_ms' column check: {e}")
            conn.rollback()

        conn.commit()
    print("\n✨ Quiz Schema Repair Complete.")

if __name__ == "__main__":
    fix_quiz_table()