from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

db_url = (
    # f"postgresql://{os.getenv('DB_USER')}:"
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:" #Async DB URL
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# Create database connection and session
# engine = create_engine(db_url, echo=True)
# engine = create_engine(db_url)
engine = create_async_engine(db_url)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base = declarative_base() This is the "old" way of doing things. Instead we do

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session   

#Database session dependency function
# def get_db():
#     with SessionLocal() as db:
#         yield db   
    # db = Session() #Create a session
    # try:
    #     yield db #Provide the session to the endpoint, and continues when it's done
    # finally:
    #     db.close() #Close the session