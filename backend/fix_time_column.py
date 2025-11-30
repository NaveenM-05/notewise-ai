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

def force_add_column():
    print("🔧 Fixing 'study_sets' table...")
    with engine.connect() as conn:
        try:
            # 1. Try to add the column directly
            conn.execute(text("ALTER TABLE study_sets ADD COLUMN total_time_studied INTEGER DEFAULT 0"))
            print("   ✅ SUCCESS: Created 'total_time_studied' column.")
        except Exception as e:
            # 2. If it fails, it might already exist or have a different name
            print(f"   ⚠️ Error adding column (might already exist): {e}")
            conn.rollback()
            
            # 3. Double check if it exists now
            try:
                result = conn.execute(text("SELECT total_time_studied FROM study_sets LIMIT 1"))
                print("   ✅ VERIFIED: The column exists now.")
            except Exception as e2:
                print(f"   ❌ CRITICAL: Still cannot see the column. Details: {e2}")

        conn.commit()
    print("\n✨ Fix script finished.")

if __name__ == "__main__":
    force_add_column()