from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database Setup ---
# Replace with your actual PostgreSQL credentials
# Format: "postgresql://USER:PASSWORD@HOST/DB_NAME"
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/notewise_db"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class
# Each instance of SessionLocal will be a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# Our database models will inherit from this class
Base = declarative_base()

# --- Dependency ---
# We will use this dependency in our API endpoints
# to get a database session for each request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()