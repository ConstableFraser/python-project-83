import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


def get_db():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')

    return psycopg2.connect(DATABASE_URL)
