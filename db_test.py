from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_url = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
# postgresql://username:password@host:port/database_name

# engine = create_engine(db_url, echo=True)
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Connected succesfully!")
        print(f"PostgreSQL version: {result.fetchone()[0]}")
        query = conn.execute(text("SELECT * FROM cars"))
        for row in query.fetchall():
            print(row)
        # conn.commit() ONLY WHEN MAKING CHANGES
except Exception as e:
    print(f"Connection failed: {e}")

engine.dispose()
print("Engine disposed, all connections closed")
