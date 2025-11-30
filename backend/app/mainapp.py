import os
import base64
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4
from importlib import import_module

from fastapi import FastAPI, Depends, HTTPException, Request, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func

# ---------------------------------------------------------
# Import internal modules
# ---------------------------------------------------------
try:
    from app import database, models, security, ai_engine
    from app.database import get_db, engine, Base
    # IMPORT NEW AI FUNCTIONS
    from app.ai_engine import generate_quiz_from_context, grade_arena_submission
except ImportError:
    import database, models, security, ai_engine
    from database import get_db, engine, Base
    from ai_engine import generate_quiz_from_context, grade_arena_submission

app = FastAPI(title="Notewise AI Backend")

# ---------------------------------------------------------
# Auth Bypass / Dev User Logic
# ---------------------------------------------------------
def _find_get_current_user_functions():
    candidates = [
        ("app.security", ["get_current_user", "get_current_active_user"]),
        ("security", ["get_current_user", "get_current_active_user"]),
        ("app.auth", ["get_current_user"]),
        ("auth", ["get_current_user"])
    ]
    found = []
    for mod_name, names in candidates:
        try:
            mod = import_module(mod_name)
        except Exception:
            continue
        for n in names:
            fn = getattr(mod, n, None)
            if callable(fn):
                found.append(fn)
    return found

def _dev_get_current_user():
    target_id = int(os.getenv("DEV_USER_ID", "1"))
    db = None
    try:
        db = database.SessionLocal()
        user = db.query(models.User).filter(models.User.id == target_id).first()
        if user: return user
        class _U:
            id = target_id
            email = "dev@local"
            is_active = True
        return _U()
    finally:
        if db: db.close()

if os.environ.get("DEV_BYPASS_AUTH") == "1":
    print(f"⚠️  AUTH BYPASS ENABLED. User ID: {os.environ.get('DEV_USER_ID', '1')}")
    funcs = _find_get_current_user_functions()
    for fn in funcs:
        try:
            app.dependency_overrides[fn] = _dev_get_current_user
        except Exception:
            pass

# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------
origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins] if origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"🔥 Unhandled server error: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class StartArenaSessionPayload(BaseModel):
    set_id: int
    num_questions: int = 1

class QuizCompletePayload(BaseModel):
    set_id: int
    session_id: Optional[int] = None
    answers: List[Dict[str, Any]]
    
class ReviewPayload(BaseModel):
    card_id: int
    difficulty: str  # "again", "hard", "good", "easy"

class ArenaSubmitPayload(BaseModel):
    set_id: int
    challenge_id: int
    user_response: str # CHANGED: Now accepts text response

# ---------------------------------------------------------
# Dependencies
# ---------------------------------------------------------
def get_current_user(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    return security.get_current_user(token=token, db=db)

# ---------------------------------------------------------
# API Routes
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "service": "Notewise AI Backend"}

# --- AUTH ROUTES ---
@app.post("/api/register", status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/api/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Study Sets ---

@app.get("/api/study-sets")
def get_study_sets(db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    sets = db.query(models.StudySet).filter(models.StudySet.user_id == current_user.id).all()
    out = []
    for s in sets:
        out.append({
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "card_count": s.card_count,
            "mastery_score": s.mastery_score,
            "srs_success_rate": s.srs_success_rate,
            "created_at": s.created_at.isoformat() if s.created_at else None
        })
    return out

@app.delete("/api/study-sets/{set_id}", status_code=204)
def delete_study_set(set_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    study_set = db.query(models.StudySet).filter(models.StudySet.id == set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")
    
    # Cascade delete handles relations usually, but manual cleanup is safe
    db.delete(study_set)
    db.commit()
    return None

@app.get("/api/reviews/today")
def get_reviews_today(db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    now = datetime.utcnow()
    
    results = db.query(
        models.StudySet.id,
        models.StudySet.title,
        func.count(models.Flashcard.id).label("due_count")
    ).join(models.Flashcard)\
    .filter(models.StudySet.user_id == current_user.id)\
    .filter(
        (models.Flashcard.next_review_date <= now) | 
        (models.Flashcard.next_review_date == None)
    ).group_by(models.StudySet.id).all()
    
    out = []
    for r in results:
        out.append({
            "setId": r.id,
            "title": r.title,
            "dueCardCount": r.due_count
        })
        
    return out

# --- Generation ---

@app.post("/api/generate")
async def generate(
    title: str = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    try:
        pdf_bytes = await file.read()
        final_title = title or f"Study Set {datetime.utcnow().isoformat()}"
        
        extracted_text = ai_engine.extract_text_from_pdf(pdf_bytes)
        syllabus = ai_engine.generate_syllabus(extracted_text)
        if not syllabus:
            raise HTTPException(status_code=503, detail="AI failed to generate syllabus")

        study_set = models.StudySet(
            title=final_title, 
            description="Generated from PDF", 
            user_id=current_user.id, 
            created_at=datetime.utcnow()
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)

        total_cards = 0

        for topic in syllabus:
            topic_content = ai_engine.generate_content_for_topic(topic)
            if not topic_content: continue

            for fc in topic_content.get("flashcards", []):
                frow = models.Flashcard(
                    set_id=study_set.id,
                    question=fc.get("question"),
                    answer=fc.get("answer"),
                    tag=fc.get("tag")
                )
                db.add(frow)
                total_cards += 1

            quiz = topic_content.get("quiz")
            if quiz:
                qrow = models.QuizQuestion(
                    set_id=study_set.id,
                    question=quiz.get("question"),
                    options=quiz.get("options") or [],
                    correct_answer=quiz.get("correct_answer"),
                    tag=quiz.get("tag")
                )
                db.add(qrow)

            arena = topic_content.get("arena")
            if arena:
                arow = models.ArenaChallenge(
                    set_id=study_set.id,
                    scenario=arena.get("scenario"),
                    ideal_response=arena.get("ideal_response"),
                    related_topic_tag=arena.get("related_topic_tag")
                )
                db.add(arow)
            db.commit()

        study_set.card_count = total_cards
        db.commit()

        return {"set_id": study_set.id, "title": study_set.title, "cards_created": total_cards}

    except HTTPException: raise
    except Exception as e:
        print(f"🔥 CRITICAL ERROR in /api/generate: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# --- Flashcards ---

@app.get("/api/study-set/{set_id}/flashcards")
def get_flashcards(
    set_id: int, 
    mode: str = "all", 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(security.get_current_user)
):
    study_set = db.query(models.StudySet).filter(models.StudySet.id == set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")
    
    query = db.query(models.Flashcard).filter(models.Flashcard.set_id == set_id)
    
    if mode == "due":
        now = datetime.utcnow()
        query = query.filter(
            (models.Flashcard.next_review_date <= now) | 
            (models.Flashcard.next_review_date == None)
        )
        
    frows = query.all()
    
    return [{
        "id": f.id, 
        "question": f.question, 
        "answer": f.answer, 
        "tag": f.tag,
        "repetition_number": f.repetition_number, 
        "interval": f.interval, 
        "ease_factor": f.ease_factor,
        "next_review_date": f.next_review_date.isoformat() if f.next_review_date else None
    } for f in frows]

# --- SRS Review Endpoint ---
@app.post("/api/flashcards/review")
def review_flashcard(payload: ReviewPayload, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    """
    Updates the flashcard's SRS data (SM-2 Algorithm) based on user difficulty rating.
    """
    card = db.query(models.Flashcard).filter(models.Flashcard.id == payload.card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # 1. Map difficulty string to Quality score (0-5)
    # again=0, hard=3, good=4, easy=5
    quality_map = {"again": 0, "hard": 3, "good": 4, "easy": 5}
    quality = quality_map.get(payload.difficulty, 4)

    # 2. Apply SM-2 Algorithm Logic
    if quality < 3: # "Again" - Reset progress
        card.repetition_number = 0
        card.interval = 1
    else:
        if card.repetition_number == 0:
            card.interval = 1
        elif card.repetition_number == 1:
            card.interval = 6
        else:
            card.interval = int(card.interval * card.ease_factor)
        
        card.repetition_number += 1
        
        # Adjust Ease Factor
        # EF' = EF + (0.1 - (5-q) * (0.08 + (5-q)*0.02))
        card.ease_factor = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if card.ease_factor < 1.3:
            card.ease_factor = 1.3

    # 3. Set Next Review Date
    card.next_review_date = datetime.utcnow() + timedelta(days=card.interval)
    
    db.commit()
    
    return {
        "status": "success", 
        "new_interval": card.interval,
        "next_review": card.next_review_date.isoformat()
    }
    
# --- Quiz ---

@app.get("/api/quiz/{set_id}")
def get_quiz_by_set(set_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    study_set = db.query(models.StudySet).filter(models.StudySet.id == set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")
        
    quiz_rows = db.query(models.QuizQuestion).filter(models.QuizQuestion.set_id == set_id).all()
    # Optional: If no quiz found, maybe trigger auto-generation? For now return empty or 404
    if not quiz_rows:
        return []
        
    return [{"id": q.id, "question": q.question, "options": q.options, "correct_answer": q.correct_answer, "tag": q.tag} for q in quiz_rows]

@app.post("/api/quiz/complete")
def quiz_complete(payload: QuizCompletePayload, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    try:
        study_set = db.query(models.StudySet).filter(models.StudySet.id == payload.set_id, models.StudySet.user_id == current_user.id).first()
        if not study_set:
            raise HTTPException(status_code=404, detail="Study set not found")
        
        correct = 0
        user_answers_map = {ans['question_id']: ans['selected'] for ans in payload.answers}
        quiz_questions = db.query(models.QuizQuestion).filter(models.QuizQuestion.set_id == payload.set_id).all()
        
        for q in quiz_questions:
            user_selected = user_answers_map.get(q.id)
            if user_selected and user_selected == q.correct_answer:
                correct += 1
        
        if quiz_questions:
            score_pct = (correct / len(quiz_questions)) * 100
            study_set.mastery_score = score_pct 
        
        if hasattr(models, 'QuizSession'):
            session_row = models.QuizSession(
                user_id=current_user.id,
                set_id=payload.set_id,
                score=correct,
                answers=payload.answers, 
                duration_ms=0 
            )
            db.add(session_row)
            db.commit()

        return {"set_id": payload.set_id, "answered": len(payload.answers), "correct": correct}
    except Exception as e:
        print(f"Error in /api/quiz/complete: {e}")
        raise HTTPException(status_code=500, detail="Server error")

# --- NEW: Quiz Regeneration ---
@app.post("/api/quiz/regenerate/{set_id}")
def regenerate_quiz(set_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    study_set = db.query(models.StudySet).filter(models.StudySet.id == set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")

    flashcards = db.query(models.Flashcard).filter(models.Flashcard.set_id == set_id).all()
    if not flashcards:
        raise HTTPException(status_code=400, detail="No flashcards available to generate quiz from.")
    
    context_text = "\n".join([f"Q: {f.question}\nA: {f.answer}" for f in flashcards])

    # Call AI
    new_questions_data = generate_quiz_from_context(context_text, num_questions=5)
    
    if not new_questions_data:
        raise HTTPException(status_code=503, detail="AI failed to generate quiz")

    # Replace old questions
    db.query(models.QuizQuestion).filter(models.QuizQuestion.set_id == set_id).delete()
    
    for q in new_questions_data:
        new_q = models.QuizQuestion(
            set_id=set_id,
            question=q["question"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            tag="Generated"
        )
        db.add(new_q)
    
    db.commit()
    
    return {"message": "Quiz regenerated successfully", "count": len(new_questions_data)}

# --- Arena ---

@app.get("/api/arena/{set_id}")
def get_arena_challenge_by_set(set_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    study_set = db.query(models.StudySet).filter(models.StudySet.id == set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")
        
    arena_row = db.query(models.ArenaChallenge).filter(models.ArenaChallenge.set_id == set_id).first()
    if not arena_row:
        # Fallback empty or 404
        raise HTTPException(status_code=404, detail="No Application Scenario found for this study set")
        
    return {"id": arena_row.id, "scenario": arena_row.scenario, "ideal_response": arena_row.ideal_response, "related_topic_tag": arena_row.related_topic_tag, "set_id": arena_row.set_id}

@app.post("/api/arena/session/start")
def start_arena_session(payload: StartArenaSessionPayload, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    study_set = db.query(models.StudySet).filter(models.StudySet.id == payload.set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")

    session_row = models.ArenaSession(set_id=payload.set_id, user_id=current_user.id, created_at=datetime.utcnow(), meta={})
    db.add(session_row)
    db.commit()
    db.refresh(session_row)

    generation_kwargs = {"temperature": 0.8, "top_p": 0.95, "random_seed": str(uuid4()), "num_questions": max(1, min(10, payload.num_questions))}

    try:
        generated = ai_engine.generate_arena_questions_for_set(study_set, generation_kwargs)
    except Exception as e:
        db.delete(session_row)
        db.commit()
        raise HTTPException(status_code=503, detail=f"AI generation failed: {e}")

    saved_questions = []
    for item in generated:
        qrow = models.ArenaSessionQuestion(
            session_id=session_row.id, set_id=payload.set_id,
            question_text=item.get("scenario") or item.get("question") or "",
            ideal_response=item.get("ideal_response") or item.get("answer") or "",
            question_meta=item.get("meta", {}),
            created_at=datetime.utcnow()
        )
        db.add(qrow)
        saved_questions.append(qrow)
    db.commit()

    return {
        "session_id": session_row.id,
        "created_at": session_row.created_at.isoformat(),
        "questions": [{"id": q.id, "question_text": q.question_text, "ideal_response": q.ideal_response, "meta": q.question_meta} for q in saved_questions]
    }

@app.get("/api/arena/session/{session_id}")
def get_arena_session(session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    session_row = db.query(models.ArenaSession).filter(models.ArenaSession.id == session_id, models.ArenaSession.user_id == current_user.id).first()
    if not session_row: raise HTTPException(status_code=404, detail="Arena session not found")
    qrows = db.query(models.ArenaSessionQuestion).filter(models.ArenaSessionQuestion.session_id == session_row.id).all()
    return {
        "session_id": session_row.id, "created_at": session_row.created_at.isoformat(),
        "questions": [{"id": q.id, "question_text": q.question_text, "ideal_response": q.ideal_response, "meta": q.question_meta} for q in qrows]
    }

# --- UPDATED: Arena Submit with AI Grading ---
@app.post("/api/arena/submit")
def submit_arena_assessment(payload: ArenaSubmitPayload, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    study_set = db.query(models.StudySet).filter(models.StudySet.id == payload.set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")
        
    challenge = db.query(models.ArenaChallenge).filter(models.ArenaChallenge.id == payload.challenge_id).first()
    scenario_text = challenge.scenario if challenge else "General Context"

    # Call AI Grading
    print(f"🤖 Grading Arena submission for User {current_user.id}...")
    grading_result = grade_arena_submission(scenario_text, payload.user_response)
    
    return {
        "status": "success", 
        "ai_score": grading_result.get("score", 0),
        "ai_feedback": grading_result.get("feedback", "No feedback.")
    }
    
@app.post("/api/arena/regenerate/{set_id}")
def regenerate_arena_challenge(set_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    """
    Generates a FRESH Arena scenario and updates the database.
    """
    study_set = db.query(models.StudySet).filter(models.StudySet.id == set_id, models.StudySet.user_id == current_user.id).first()
    if not study_set:
        raise HTTPException(status_code=404, detail="Study set not found")

    print(f"🔄 Regenerating Arena Scenario for Set {set_id}...")

    # 1. Call AI to generate 1 new scenario
    # We use a random seed to ensure it's different from the last one
    gen_kwargs = {"num_questions": 1, "random_seed": str(uuid4())}
    new_scenarios = ai_engine.generate_arena_questions_for_set(study_set, gen_kwargs)
    
    if not new_scenarios:
        raise HTTPException(status_code=503, detail="AI failed to generate new scenario")

    new_data = new_scenarios[0]

    # 2. Update the existing record in DB
    arena_row = db.query(models.ArenaChallenge).filter(models.ArenaChallenge.set_id == set_id).first()
    if arena_row:
        arena_row.scenario = new_data["scenario"]
        arena_row.ideal_response = new_data["ideal_response"]
        # Update tag if available
        if "meta" in new_data and "topic" in new_data["meta"]:
             arena_row.related_topic_tag = new_data["meta"]["topic"]
    else:
        # Create if missing
        arena_row = models.ArenaChallenge(
            set_id=set_id,
            scenario=new_data["scenario"],
            ideal_response=new_data["ideal_response"],
            related_topic_tag="General"
        )
        db.add(arena_row)

    db.commit()
    return {"status": "success", "message": "New scenario generated"}