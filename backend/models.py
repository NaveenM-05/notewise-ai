from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship: A user can own many study sets
    study_sets = relationship("StudySet", back_populates="owner")

class StudySet(Base):
    __tablename__ = "study_sets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="study_sets")
    flashcards = relationship("Flashcard", back_populates="study_set", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="study_set", cascade="all, delete-orphan")
    arena_challenges = relationship("ArenaChallenge", back_populates="study_set", cascade="all, delete-orphan")

class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    
    # --- Algorithm-Specific Fields ---
    sub_topic_tag = Column(String, index=True, nullable=False)
    next_review_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    interval = Column(Float, default=0.0) # In days
    ease_factor = Column(Float, default=2.5)
    # -----------------------------------
    
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    study_set = relationship("StudySet", back_populates="flashcards")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=False) # e.g., ["Option A", "Option B", "Option C"]
    correct_answer = Column(String, nullable=False) # e.g., "Option A"
    
    # --- Algorithm-Specific Field ---
    sub_topic_tag = Column(String, index=True, nullable=False)
    # ---------------------------------
    
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    study_set = relationship("StudySet", back_populates="quiz_questions")

class ArenaChallenge(Base):
    __tablename__ = "arena_challenges"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    scenario_description = Column(String, nullable=False) # The real-world problem
    
    # --- Algorithm-Specific Field ---
    sub_topic_tag = Column(String, index=True, nullable=False)
    # ---------------------------------
    
    set_id = Column(Integer, ForeignKey("study_sets.id"))
    study_set = relationship("StudySet", back_populates="arena_challenges")