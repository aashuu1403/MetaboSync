from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# We are using SQLite for instant testing today. 
# To upgrade to PostgreSQL later, we simply change this one line.
SQLALCHEMY_DATABASE_URL = "sqlite:///./metabosync.db"

# Create the database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session in our API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()