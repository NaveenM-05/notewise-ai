from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean, Float, BigInteger
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)  # This must match 'password_hash' in mainapp.py

    study_sets = relationship("StudySet", back_populates="owner")

class StudySet(Base):
    __tablename__ = "study_sets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    pdf_filename = Column(String, nullable=True)
    
    # Stats
    card_count = Column(Integer, default=0)
    mastery_score = Column(Float, default=0.0)
    srs_success_rate = Column(Float, default=0.0)
    total_time_studied = Column(Integer, default=0) # milliseconds
    
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="study_sets")
    flashcards = relationship("Flashcard", back_populates="study_set", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="study_set", cascade="all, delete-orphan")
    arena_challenges = relationship("ArenaChallenge", back_populates="study_set", cascade="all, delete-orphan")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    question = Column(Text)
    answer = Column(Text)
    tag = Column(String, nullable=True)

    # SRS Fields
    repetition_number = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Float, default=0.0)
    next_review_date = Column(DateTime, nullable=True)
    
    study_set = relationship("StudySet", back_populates="flashcards")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    question = Column(Text)
    options = Column(JSON)  # List of strings
    correct_answer = Column(String)
    tag = Column(String, nullable=True)

    study_set = relationship("StudySet", back_populates="quiz_questions")

class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # <--- ADDED THIS
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    score = Column(Integer, default=0)
    answers = Column(JSON)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class ArenaChallenge(Base):
    __tablename__ = "arena_challenges"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    scenario = Column(Text)
    ideal_response = Column(Text)
    related_topic_tag = Column(String, nullable=True)

    study_set = relationship("StudySet", back_populates="arena_challenges")

class ArenaSession(Base):
    __tablename__ = "arena_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON, nullable=True)
    
    questions = relationship("ArenaSessionQuestion", back_populates="session", cascade="all, delete-orphan")

class ArenaSessionQuestion(Base):
    __tablename__ = "arena_session_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("arena_sessions.id"))
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    
    question_text = Column(Text)
    ideal_response = Column(Text)
    # RENAMED from 'metadata' to 'question_meta' to avoid SQLAlchemy conflict
    question_meta = Column(JSON, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ArenaSession", back_populates="questions")