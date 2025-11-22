from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Date, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    study_sets = relationship("StudySet", back_populates="owner")

class StudySet(Base):
    __tablename__ = "study_sets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    pdf_filename = Column(String)
    
    # Metrics for the "Unified Mastery Algorithm"
    card_count = Column(Integer, default=0)
    mastery_score = Column(Float, default=0.0) # Macro-level score (0-100)
    srs_success_rate = Column(Float, default=75.0) # Retention score
    total_time_studied_ms = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="study_sets")
    flashcards = relationship("Flashcard", back_populates="study_set")
    quiz_questions = relationship("QuizQuestion", back_populates="study_set")
    arena_challenges = relationship("ArenaChallenge", back_populates="study_set")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    
    question = Column(Text)
    answer = Column(Text)
    tag = Column(String, index=True) # Sub-topic tag for granular scheduling

    # SM-2 Algorithm Fields
    repetition_number = Column(Integer, default=0)
    interval = Column(Float, default=0.0) # Days
    ease_factor = Column(Float, default=2.5)
    next_review_date = Column(Date, default=func.current_date())

    study_set = relationship("StudySet", back_populates="flashcards")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    
    question = Column(Text)
    options = Column(JSON) # Stored as a JSON list of strings
    correct_answer = Column(String)
    tag = Column(String) # Sub-topic tag

    study_set = relationship("StudySet", back_populates="quiz_questions")

class ArenaChallenge(Base):
    __tablename__ = "arena_challenges"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    
    scenario = Column(Text)
    ideal_response = Column(Text)
    related_topic_tag = Column(String) # Links to flashcards

    study_set = relationship("StudySet", back_populates="arena_challenges")