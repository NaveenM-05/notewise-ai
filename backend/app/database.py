from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 1. Load the .env file explicitly
load_dotenv()

# 2. Get the URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Check if it exists (Prevent the "user" error)
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Please check your .env file.")

# 4. Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 5. Create the SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 6. Create the Base class
Base = declarative_base()

# 7. Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
