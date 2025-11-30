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

def fix_quiz_constraint():
    print("🔧 Fixing 'quiz_sessions' table constraint...")
    with engine.connect() as conn:
        try:
            # 1. Attempt to remove the NOT NULL constraint from 'questions'
            # This allows the column to be empty, so our code won't crash.
            conn.execute(text("ALTER TABLE quiz_sessions ALTER COLUMN questions DROP NOT NULL"))
            print("   ✅ SUCCESS: 'questions' column is no longer required.")
        except Exception as e:
            # If the column doesn't exist, that's actually good (means no conflict)
            if "UndefinedColumn" in str(e) or "does not exist" in str(e):
                print("   ✅ 'questions' column does not exist (No fix needed).")
            else:
                print(f"   ⚠️ Could not alter column: {e}")
                
        conn.commit()
    print("\n✨ Constraint Fix Complete.")

if __name__ == "__main__":
    fix_quiz_constraint()