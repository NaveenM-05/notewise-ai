from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Any
from datetime import datetime, date

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Flashcard Schemas ---
class FlashcardBase(BaseModel):
    question: str
    answer: str
    tag: str

class Flashcard(FlashcardBase):
    id: int
    set_id: int
    repetition_number: int
    next_review_date: date
    
    model_config = ConfigDict(from_attributes=True)

# --- Quiz Schemas ---
class QuizQuestionBase(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    tag: str

class QuizQuestion(QuizQuestionBase):
    id: int
    set_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Arena Schemas ---
class ArenaChallengeBase(BaseModel):
    scenario: str
    ideal_response: str
    related_topic_tag: str

class ArenaChallenge(ArenaChallengeBase):
    id: int
    set_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Study Set Schemas ---
class StudySetBase(BaseModel):
    title: str
    pdf_filename: str

class StudySetCreate(StudySetBase):
    pass

class StudySet(StudySetBase):
    id: int
    user_id: int
    card_count: int
    mastery_score: float
    srs_success_rate: float
    total_time_studied_ms: int
    created_at: datetime
    
    # We can optionally include lists of items if needed
    flashcards: List[Flashcard] = []
    quiz_questions: List[QuizQuestion] = []
    
    model_config = ConfigDict(from_attributes=True)
