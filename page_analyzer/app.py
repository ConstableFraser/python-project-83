import os
import secrets
import requests
import psycopg2.extras
from datetime import datetime
from validators.url import url
from urllib.parse import urlparse
from page_analyzer.db import get_db
from page_analyzer.html import get_page_contents
from flask import (Flask, render_template, request, redirect,
                   url_for, flash)


MAX_LENGTH = 255
app = Flask(__name__)


secret_key = os.getenv('SECRET_KEY')
app.secret_key = secret_key if secret_key else secrets.token_bytes(32)


@app.route('/', methods=['GET'])
def start():
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def sites():
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
        records = cur.fetchall()
        print(records)
    return render_template('urls.html', rows=records), 200


@app.post('/urls')
def add():
    address = urlparse(request.form.get('url'))
    scheme = address[0] if address[0] else 'http'
    scheme += '://'
    netloc = address[1]
    path = address[2]
    link = scheme + netloc + path

    if len(link) > MAX_LENGTH or not url(link):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = (%s)", (link,))
            records = cur.fetchone()

            if records:
                flash('Страница уже существует', 'info')
                return redirect(url_for('site', id=records[0]))

            cur.execute("INSERT INTO urls (name, created_at) \
                        VALUES (%s, %s) RETURNING id", (link, datetime.today()))
            max_id = cur.fetchone()
            conn.commit()

            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('site', id=max_id[0]))


@app.route('/urls/<id>', methods=['GET'])
def site(id):
    factory = psycopg2.extras.NamedTupleCursor
    with get_db().cursor(cursor_factory=factory) as cur:
        id = int(id) if id.isdigit() else None
        cur.execute("SELECT name FROM urls WHERE id = (%s)", (id,))
        site_name = cur.fetchone()

        if not site_name:
            flash('Такой страницы не существует', 'danger')
            return render_template('404.html'), 404

        cur.execute("SELECT id, name, created_at FROM urls \
                    WHERE id = (%s)", (id,))
        record = cur.fetchone()

        cur.execute("SELECT id, status_code, h1, title, \
                    description, created_at \
                    FROM url_checks WHERE url_id = (%s) \
                    ORDER BY id DESC", (id,))
        checks = cur.fetchall()

        return render_template('url_id.html',
                               site_name=site_name[0],
                               id=id,
                               checks=checks,
                               record=record)


@app.post('/urls/<id>/checks')
def check(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM urls WHERE id = (%s)", (id,))
            records = cur.fetchone()
            url = records[0]

            headers = requests.utils.default_headers()
            headers.update({'User-Agent': 'My User Agent 1.0'})

            try:
                response = requests.get(url, headers=headers)
            except requests.ConnectionError as e:
                flash('Произошла ошибка про проверке', 'danger')
                print(e)
                return redirect(url_for('site', id=id), code=302)

            status_code = response.status_code

            h1 = get_page_contents(response.text, 'h1')
            title = get_page_contents(response.text, 'title')
            content = get_page_contents(response.text, 'content')

            cur.execute("INSERT INTO url_checks \
                        (url_id, status_code, h1, title, description, \
                        created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                        (id, status_code, h1, title, content, datetime.today()))
            conn.commit()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('site', id=id), code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
