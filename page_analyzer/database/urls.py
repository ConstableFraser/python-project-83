import psycopg2.extras
from datetime import datetime
from page_analyzer.database.db import get_db


def get_urls_list():
    factory = psycopg2.extras.NamedTupleCursor
    with get_db().cursor(cursor_factory=factory) as cur:
        cur.execute("SELECT \
                         urls.id AS id, urls.name AS name, \
                         url_checks.created_at as created_at, \
                         url_checks.status_code as status_code\
                     FROM urls \
                     LEFT JOIN url_checks ON urls.id = url_checks.url_id \
                     WHERE (url_checks.id IS NULL OR url_checks.id IN \
                           (SELECT MAX(id) \
                            FROM url_checks \
                            GROUP BY url_id)) \
                     ORDER BY urls.id DESC")
        return cur.fetchall()


def get_id_url_by_name(url_name):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = (%s)", (url_name,))
            records = cur.fetchone()
            return str(*records) if records else None


def get_name_url_by_id(id):
    factory = psycopg2.extras.NamedTupleCursor
    with get_db().cursor(cursor_factory=factory) as cur:
        cur.execute("SELECT name FROM urls WHERE id = (%s)", (id,))
        return cur.fetchone()


def get_url_info_by_id(id):
    factory = psycopg2.extras.NamedTupleCursor
    with get_db().cursor(cursor_factory=factory) as cur:
        cur.execute("SELECT id, name, created_at FROM urls \
                     WHERE id = (%s)", (id,))
        return cur.fetchone()


def add_new_url(name):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name, created_at) \
                         VALUES (%s, %s) RETURNING id",
                        (name, datetime.today()))
            id = cur.fetchone()
            conn.commit()
            return str(*id)
