import sys
import os
from datetime import datetime

# Setup import path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app import models

def check_schedule():
    db = SessionLocal()
    print(f"\n📅 --- SRS SCHEDULING REPORT ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n")
    
    # Get all flashcards for user 2 (since we are bypassing auth as user 2)
    # Note: In a real scenario, you'd filter by specific user. 
    # Here we just grab all cards to see what's happening.
    cards = db.query(models.Flashcard).all()

    if not cards:
        print("❌ No flashcards found in database.")
        return

    print(f"{'ID':<5} | {'Interval':<10} | {'Next Review':<25} | {'Question (Snippet)'}")
    print("-" * 80)

    for card in cards:
        # Format date or show 'Not Set'
        review_date = "Not Scheduled"
        if card.next_review_date:
            review_date = card.next_review_date.strftime('%Y-%m-%d %H:%M')
        
        snippet = (card.question[:30] + '...') if len(card.question) > 30 else card.question
        
        print(f"{card.id:<5} | {card.interval:<10} | {review_date:<25} | {snippet}")

    print("\n--------------------------------------------------------------------------------")
    print("NOTE: 'Interval' is in days. If 'Next Review' is in the future, it won't appear on Dashboard.")

if __name__ == "__main__":
    check_schedule()