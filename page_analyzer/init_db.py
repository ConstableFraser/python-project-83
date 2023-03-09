import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()
dbname = os.getenv("DBNAME")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")


def get_db():
    print("DBNAME:\t", dbname)
    print("USER:\t", user)
    return psycopg2.connect(dbname=dbname,
                            user=user,
                            password=password,
                            host=host)


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS url_checks")
    cur.execute("DROP TABLE IF EXISTS urls")

    cur.execute("CREATE TABLE urls( \
                 id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, \
                 name varchar(255) UNIQUE NOT NULL, \
                 created_at float)")

    cur.execute("CREATE TABLE url_checks( \
                 id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, \
                 url_id bigint REFERENCES urls (id), \
                 status_code integer, \
                 h1 text, \
                 title varchar(255), \
                 description text, \
                 created_at float)")

    conn.commit()
    cur.close()
    conn.close()
