import time
import requests
from datetime import datetime
from validators.url import url
from urllib.parse import urlparse
from page_analyzer.rand import get_random
from page_analyzer.init_db import get_db, init_db
from page_analyzer.find_value_html import get_value
from flask import (Flask, render_template, request, redirect,
                   url_for, flash)


MAX_LENGTH = 255
app = Flask(__name__)

app.secret_key = get_random()
init_db()


@app.route('/', methods=['GET'])
def start():
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def sites():
    with get_db().cursor() as cur:
        cur.execute("SELECT urls.id, urls.name, url_checks.created_at, \
                    url_checks.status_code FROM urls LEFT JOIN url_checks ON \
                    urls.id = url_checks.url_id WHERE \
                    (url_checks.id IS NULL OR url_checks.id IN \
                    (SELECT id FROM url_checks WHERE created_at IN \
                    (SELECT MAX(created_at) FROM url_checks GROUP BY \
                    url_id))) ORDER BY urls.id DESC")
        records = cur.fetchall()
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
                        VALUES ((%s), (%s)) RETURNING id", (link, time.time()))
            max_id = cur.fetchone()
            conn.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('site', id=max_id[0]))


@app.route('/urls/<id>', methods=['GET'])
def site(id):
    with get_db().cursor() as cur:
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

            h1 = get_value(response.text, 'h1')
            title = get_value(response.text, 'title')
            content = get_value(response.text, 'content')

            cur.execute("INSERT INTO url_checks \
                        (url_id, status_code, h1, title, description, \
                        created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                        (id, status_code, h1, title, content, time.time()))
            conn.commit()
    return redirect(url_for('site', id=id), code=302)


@app.template_filter('date')
def timectime(timestamp):
    if timestamp is not None:
        return datetime.date(datetime.fromtimestamp(timestamp))
    else:
        return ""


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
