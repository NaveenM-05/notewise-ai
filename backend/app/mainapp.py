from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Import your custom modules
from . import models, schemas, security, database, ai_engine

# --- Create Database Tables ---
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="NoteWise AI Backend")

# --- CORS Middleware ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for getting a DB session
get_db = database.get_db

# --------------------------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# --------------------------------------------------------------------------

@app.post("/api/register", response_model=schemas.UserInDB)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = security.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = security.get_user(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=schemas.UserInDB)
async def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user

# --------------------------------------------------------------------------
# AI GENERATION & STUDY SET ENDPOINTS
# --------------------------------------------------------------------------

@app.post("/api/generate", response_model=schemas.StudySet)
async def generate_study_set(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    pdf_content = await file.read()
    text = ai_engine.extract_text_from_pdf(pdf_content)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    syllabus = ai_engine.generate_syllabus(text)
    if not syllabus:
        raise HTTPException(status_code=500, detail="AI failed to generate a syllabus.")

    new_set = models.StudySet(
        user_id=current_user.id,
        title=file.filename.replace(".pdf", ""),
        pdf_filename=file.filename
    )
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    
    total_cards = 0
    for topic_data in syllabus:
        content = ai_engine.generate_content_for_topic(topic_data)
        if content:
            for card_data in content.get('flashcards', []):
                flashcard = models.Flashcard(
                    set_id=new_set.id,
                    question=card_data['question'],
                    answer=card_data['answer'],
                    tag=card_data.get('tag', topic_data['topic'])
                )
                db.add(flashcard)
                total_cards += 1
            
            q_data = content.get('quiz')
            if q_data:
                quiz = models.QuizQuestion(
                    set_id=new_set.id,
                    question=q_data['question'],
                    options=q_data['options'],
                    correct_answer=q_data['correct_answer'],
                    tag=q_data.get('tag', topic_data['topic'])
                )
                db.add(quiz)
            
            a_data = content.get('arena')
            if a_data:
                arena = models.ArenaChallenge(
                    set_id=new_set.id,
                    scenario=a_data['scenario'],
                    ideal_response=a_data['ideal_response'],
                    related_topic_tag=a_data.get('related_topic_tag', topic_data['topic'])
                )
                db.add(arena)

    new_set.card_count = total_cards
    db.commit()
    db.refresh(new_set)
    return new_set

@app.get("/api/study-sets", response_model=List[schemas.StudySet])
async def get_study_sets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    return db.query(models.StudySet).filter(models.StudySet.user_id == current_user.id).all()

# --------------------------------------------------------------------------
# CONTENT RETRIEVAL ENDPOINTS (NEW)
# --------------------------------------------------------------------------

@app.get("/api/study-set/{set_id}/flashcards", response_model=List[schemas.Flashcard])
async def get_flashcards(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    cards = db.query(models.Flashcard).filter(models.Flashcard.set_id == set_id).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No flashcards found for this set")
    return cards

@app.get("/api/quiz/{set_id}", response_model=List[schemas.QuizQuestion])
async def get_quiz(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    questions = db.query(models.QuizQuestion).filter(models.QuizQuestion.set_id == set_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No quiz found for this set")
    return questions

@app.get("/api/arena/{set_id}", response_model=schemas.ArenaChallenge)
async def get_arena(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Fetch the first available arena challenge for this set
    challenge = db.query(models.ArenaChallenge).filter(models.ArenaChallenge.set_id == set_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="No arena challenge found")
    return challenge

@app.get("/api/reviews/today", response_model=List[dict])
async def get_todays_review(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Placeholder logic: Return all sets as due for now
    # (We will update this with the real SRS query in the next phase)
    study_sets = db.query(models.StudySet).filter(models.StudySet.user_id == current_user.id).all()
    review_list = []
    for s in study_sets:
        review_list.append({
            "setId": str(s.id),
            "title": s.title,
            "dueCardCount": s.card_count 
        })
    return review_list