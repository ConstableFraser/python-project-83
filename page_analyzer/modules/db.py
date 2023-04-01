import os
import psycopg2
from dotenv import load_dotenv

SELECT = {"URL_list": "SELECT \
                          urls.id AS id, urls.name AS name, \
                          url_checks.created_at as created_at, \
                          url_checks.status_code as status_code\
                       FROM urls \
                       LEFT JOIN url_checks ON urls.id = url_checks.url_id \
                       WHERE (url_checks.id IS NULL OR url_checks.id IN \
                              (SELECT MAX(id) \
                               FROM url_checks \
                               GROUP BY url_id)) \
                       ORDER BY urls.id DESC",
          "URL_id": "SELECT id FROM urls WHERE name = (%s)",
          "URL_name": "SELECT name FROM urls WHERE id = (%s)",
          "URL_info": "SELECT id, name, created_at FROM urls \
                       WHERE id = (%s)",
          "CHECKS_url_id": "SELECT id, status_code, h1, title, \
                              description, created_at \
                            FROM url_checks WHERE url_id = (%s) \
                            ORDER BY id DESC"
          }

INSERT = {"URL_row": "INSERT INTO urls (name, created_at) \
                      VALUES (%s, %s) RETURNING id",
          "CHECKS_row": "INSERT INTO url_checks \
                             (url_id, status_code, h1, title, description, \
                              created_at) \
                         VALUES (%s, %s, %s, %s, %s, %s)"
          }


def get_db():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')

    return psycopg2.connect(DATABASE_URL)
