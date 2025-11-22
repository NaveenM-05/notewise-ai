import sys
import os

# Setup path to import from 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import StudySet, User, Flashcard

db = SessionLocal()

print("--- DATABASE CHECK ---")

# 1. Check Users
users = db.query(User).all()
print(f"\nUsers Found: {len(users)}")
for u in users:
    print(f" - ID: {u.id} | Email: {u.email}")

# 2. Check Study Sets
sets = db.query(StudySet).all()
print(f"\nStudy Sets Found: {len(sets)}")
for s in sets:
    print(f" - ID: {s.id} | Title: '{s.title}' | Owner ID: {s.user_id} | Cards: {s.card_count}")

# 3. Check Flashcards
cards = db.query(Flashcard).all()
print(f"\nTotal Flashcards: {len(cards)}")

db.close()