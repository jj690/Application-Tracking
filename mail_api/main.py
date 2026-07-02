from fastapi import FastAPI
from contextlib import contextmanager
from mail_model import E_Mail
from sql_handler import SQLHandler
import psycopg
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()


@app.post("/api/classify_email")
def classify_email_post(email: E_Mail):
    if email.is_possibly_relevant():
        classification = email.classify()
        with psycopg.connect(os.getenv("DATABASE_URL")) as db_connection:
            db_handler = SQLHandler(db_connection)
            db_handler.insert_email(classification)
            return {"classified": "True"}
    return {"classified": "False"}


@app.get("/api/database")
def get_database():
    with psycopg.connect(os.getenv("DATABASE_URL")) as db_connection:
        db_handler = SQLHandler(db_connection)
        return (db_handler.get_all_emails(),)


@app.post("/api/save_changes")
def save_changes(df: list[dict]):
    with psycopg.connect(os.getenv("DATABASE_URL")) as db_connection:
        db_handler = SQLHandler(db_connection)
        db_handler.save_changes(df)
