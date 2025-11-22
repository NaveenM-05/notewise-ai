import sys
import os

# 1. Add the current directory to the python path so we can find 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Correct Imports (Notice we just say 'app')
from app.database import engine, Base
from app import models

# 3. Reset Logic
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("✅ Tables dropped.")

print("Recreating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables recreated successfully with new schema.")
