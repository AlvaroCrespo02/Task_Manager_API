from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

db_url = (
    f"postgresql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# Create database connection
engine = create_engine(db_url, echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()

#Database session dependency function
def get_db():
    db = Session() #Create a session
    try:
        yield db #Provide the session to the endpoint, and continues when it's done
    finally:
        db.close() #Close the session