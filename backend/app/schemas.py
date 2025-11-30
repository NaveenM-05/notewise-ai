from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Any, Dict
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
    tag: Optional[str] = None  # tag can be optional

class Flashcard(FlashcardBase):
    id: int
    set_id: int
    repetition_number: int
    next_review_date: Optional[date] = None

    # Scheduling/debug fields exposed to API
    interval: Optional[float] = None
    ease_factor: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

# --- Quiz Schemas ---
class QuizQuestionBase(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    tag: Optional[str] = None

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

    flashcards: List[Flashcard] = []
    quiz_questions: List[QuizQuestion] = []

    model_config = ConfigDict(from_attributes=True)

class ReviewCardRequest(BaseModel):
    card_id: int
    difficulty: str

class QuizCompleteRequest(BaseModel):
    set_id: int
    score: float

class ArenaSubmitRequest(BaseModel):
    set_id: int
    challenge_id: int
    self_score: float

class LogTimeRequest(BaseModel):
    set_id: int
    time_spent_ms: int

# ============================================================
# NEW: FRESH QUIZ SESSION + ARENA SESSION SCHEMAS
# ============================================================

class QuizSessionCreate(BaseModel):
    set_id: int
    num_questions: int = 8  # default

class QuizSessionOut(BaseModel):
    session_id: int
    questions: List[Dict[str, Any]]

class QuizAnswerIn(BaseModel):
    session_id: int
    question_index: int
    selected: Any

class ArenaStartRequest(BaseModel):
    set_id: int
    difficulty: str  # "easy", "medium", "hard"

class ArenaStartOut(BaseModel):
    session_id: int
    challenge: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

class ArenaValidateRequest(BaseModel):
    session_id: int
    user_answer: str

