# fix_flashcards.py
import os
import sys
from sqlalchemy import create_engine, text

# Try to read DATABASE_URL from environment first (your .env) otherwise use the one you provided
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:Gok%4001@localhost:5433/notewise_db"
)

print("Using DATABASE_URL =", DATABASE_URL)

try:
    engine = create_engine(DATABASE_URL, echo=False, future=True)
except Exception as e:
    print("Error creating engine:", e)
    sys.exit(1)

update_sql = text("""
UPDATE flashcards
SET interval = 1.0,
    ease_factor = 2.5,
    repetition_number = 0
WHERE interval IS NULL OR interval = 0;
""")

check_sql = text("""
SELECT
  COUNT(*) FILTER (WHERE interval = 1.0 AND ease_factor = 2.5) as fixed_count,
  COUNT(*) as total_count
FROM flashcards;
""")

try:
    with engine.begin() as conn:
        result = conn.execute(update_sql)
        # result.rowcount may be driver-dependent, so run a count query
        check = conn.execute(check_sql).mappings().first()
        fixed = check["fixed_count"]
        total = check["total_count"]
        print(f"Update executed. Approx. rows now matching defaults: {fixed} / {total}")
except Exception as e:
    print("Error executing SQL:", e)
    sys.exit(1)

print("Done.")
