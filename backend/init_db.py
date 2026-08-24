from app.core.database import engine
from app.models.schema import Base

def init():
    print("Building MetaboSync database tables...")
    # This command looks at your schema and creates the tables in the database
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init()