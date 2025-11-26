import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = None

def connect_db():
    global conn
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Connected to PostgreSQL successfully.")
    except Exception as error:
        print("Error connecting to PostgreSQL:", error)
connect_db()