from datetime import datetime
from page_analyzer.database.db import get_db, get_cursor_tuple


def get_list(id):
    with get_cursor_tuple() as cur:
        cur.execute("SELECT id, status_code, h1, title, \
                            description, created_at \
                     FROM url_checks WHERE url_id = (%s) \
                     ORDER BY id DESC", (id,))
        return cur.fetchall()


def add_check(id, status_code, tags):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO url_checks \
                         (url_id, status_code, h1, title, description, \
                         created_at) \
                         VALUES (%s, %s, %s, %s, %s, %s)",
                        (id, status_code, tags["h1"], tags["title"],
                         tags["description"], datetime.today()))
            conn.commit()
