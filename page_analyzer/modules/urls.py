import requests
import psycopg2.extras
from datetime import datetime
from validators.url import url

from page_analyzer.modules.html import get_page_contents
from page_analyzer.modules.db import SELECT, INSERT, get_db

MAX_LENGTH = 255


def get_list_sites():
    factory = psycopg2.extras.NamedTupleCursor
    with get_db().cursor(cursor_factory=factory) as cur:
        cur.execute(SELECT["URL_list"])
        return cur.fetchall()


def normalize_url(address):
    scheme = address[0] if address[0] else 'http'
    scheme += '://'
    netloc = address[1]
    path = address[2]
    return scheme + netloc + path


def check_url(link):
    if len(link) > MAX_LENGTH or not url(link):
        return False
    return True


def check_exist(link):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT["URL_id"], (link,))
            records = cur.fetchone()

            return str(*records) if records else None


def add_site(link):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(INSERT["URL_row"], (link, datetime.today()))
            id = cur.fetchone()
            conn.commit()

            return str(*id)


def get_data_site(id):
    factory = psycopg2.extras.NamedTupleCursor
    with get_db().cursor(cursor_factory=factory) as cur:
        cur.execute(SELECT["URL_name"], (id,))
        site_name = cur.fetchone()

        if not site_name:
            return False, False

        cur.execute(SELECT["URL_info"], (id,))
        record = cur.fetchone()

        cur.execute(SELECT["CHECKS_url_id"], (id,))
        checks = cur.fetchall()

        return record, checks


def check_site(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT["URL_name"], (id,))
            records = cur.fetchone()
            url = str(*records)

            headers = requests.utils.default_headers()
            headers.update({'User-Agent': 'My User Agent 1.0'})

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except requests.RequestException:
                return False

            status_code = response.status_code

            tags = get_page_contents(response.text)

            cur.execute(INSERT["CHECKS_row"],
                        (id, status_code, tags["h1"], tags["title"],
                         tags["description"], datetime.today()))
            conn.commit()

            return True
