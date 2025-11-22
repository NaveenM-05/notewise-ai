from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware # <--- 1. NEW IMPORT
from sqlalchemy.orm import Session

import models, schemas, security, database

# --- Create Database Tables ---
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="NoteWise AI Backend")

# --- 2. ADD CORS MIDDLEWARE HERE ---
# This tells the backend to trust requests from your frontend
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
# -----------------------------------

# Dependency for getting a DB session
get_db = database.get_db

@app.post("/api/register", response_model=schemas.UserInDB)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = security.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Hash the password
    hashed_password = security.get_password_hash(user.password)
    
    # Create the new user object
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    
    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/api/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # 1. Find user in database
    user = security.get_user(db, email=form_data.username) # Form username is our email
    
    # 2. Check if user exists and password is correct
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create and return a new JWT token
    access_token = security.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Test Endpoint ---
@app.get("/api/users/me", response_model=schemas.UserInDB)
async def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user