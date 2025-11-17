from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Import all our components
from . import models, schemas, security, database

# --- Create Database Tables ---
# This command tells SQLAlchemy to create all the tables defined in models.py
# (We will eventually move to Alembic for "migrations")
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="NoteWise AI Backend")

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
# A test endpoint to show how to use the auth dependency
@app.get("/api/users/me", response_model=schemas.UserInDB)
async def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    # If the user is not authenticated, get_current_user will raise
    # an exception. If they are, it will return the user object.
    return current_user