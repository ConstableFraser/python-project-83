import os
import time
import psycopg2
import requests
from datetime import datetime
from validators.url import url
from urllib.parse import urlparse
from page_analyzer.init_db import init_db
from dotenv import load_dotenv, find_dotenv
from page_analyzer.find_value_html import get_value
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, get_flashed_messages)

app = Flask(__name__)

print("FIND_DOTENV()", find_dotenv())
load_dotenv(find_dotenv())

app.secret_key = os.environ.get("SECRETKEY")

dbname = os.environ.get("DBNAME")
user = os.environ.get("USER")
password = os.environ.get("PASSWORD")
host = os.environ.get("HOST")
print("DBNAME:", dbname)
print("USER:", user)
print("PASSWORD:", password)
print("HOST:", host)

conn = psycopg2.connect(dbname=dbname,
                        user=user,
                        password=password,
                        host=host)

cursor = conn.cursor()
init_db(cursor, conn)
cursor.close()


@app.route('/', methods=['GET'])
def start():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls', methods=['GET'])
def sites():
    cur = conn.cursor()
    cur.execute("SELECT urls.id, urls.name, url_checks.created_at, \
                url_checks.status_code FROM urls LEFT JOIN url_checks ON \
                urls.id = url_checks.url_id WHERE \
                (url_checks.id IS NULL OR url_checks.id IN \
                (SELECT id FROM url_checks WHERE created_at IN \
                (SELECT MAX(created_at) FROM url_checks GROUP BY \
                url_id))) ORDER BY urls.id DESC")
    records = cur.fetchall()
    messages = get_flashed_messages(with_categories=True)
    cur.close()
    return render_template('urls.html', messages=messages,
                           rows=records), 200


@app.post('/urls')
def add():
    address = urlparse(request.form.get('url'))
    scheme = address[0] if address[0] else 'http'
    scheme += '://'
    netloc = address[1]
    path = address[2]
    link = scheme + netloc + path
    cur = conn.cursor()
    if len(link) > 255 or not url(link):
        flash('Некорректный URL', 'danger')
        cur.close()
        return redirect(url_for('start'), code=302)

    cur.execute("SELECT id FROM urls WHERE name = (%s)", (link,))
    records = cur.fetchall()

    if records:
        flash('Страница уже существует', 'info')
        return redirect(url_for('site', id=records[0][0]), code=302)

    cur.execute("INSERT INTO urls \
                (name, created_at) \
                VALUES ((%s), (%s))", (link, time.time()))
    conn.commit()
    cur.execute("SELECT MAX(id) FROM urls")
    max_id = cur.fetchall()
    flash('Страница успешно добавлена', 'success')
    cur.close()
    return redirect(url_for('site', id=max_id[0][0]), code=302)


@app.route('/urls/<id>', methods=['GET'])
def site(id):
    cur = conn.cursor()
    id = int(id) if id.isdigit() else None
    cur.execute("SELECT name FROM urls WHERE id = (%s)", (id,))
    records = cur.fetchall()

    if not records:
        flash('Такой страницы не существует', 'danger')
        messages = get_flashed_messages(with_categories=True)
        cur.close()
        return render_template('404.html', messages=messages), 404

    site_name = records[0][0]
    cur.execute("SELECT id, name, created_at FROM urls WHERE id = (%s)", (id,))
    record = cur.fetchall()

    cur.execute("SELECT id, status_code, h1, title, description, created_at \
                 FROM url_checks WHERE url_id = (%s) \
                 ORDER BY id DESC", (id,))
    checks = cur.fetchall()

    messages = get_flashed_messages(with_categories=True)
    cur.close()
    return render_template('url_id.html',
                           messages=messages,
                           site_name=site_name,
                           id=id,
                           checks=checks,
                           record=record[0])


@app.post('/urls/<id>/checks')
def check(id):
    cur = conn.cursor()
    cur.execute("SELECT name FROM urls WHERE id = (%s)", (id,))
    records = cur.fetchall()
    url = records[0][0]

    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'My User Agent 1.0'})

    try:
        response = requests.get(url, headers=headers)
    except requests.ConnectionError as e:
        flash('Произошла ошибка про проверке', 'danger')
        print(e)
        cur.close()
        return redirect(url_for('site', id=id), code=302)

    status_code = response.status_code

    h1 = get_value(response.text, 'h1')
    title = get_value(response.text, 'title')
    content = get_value(response.text, 'content')

    cur.execute("INSERT INTO url_checks \
                (url_id, status_code, h1, title, description, created_at) \
                VALUES (%s, %s, %s, %s, %s, %s)",
                (id, status_code, h1, title, content, time.time()))
    conn.commit()
    cur.close()

    return redirect(url_for('site', id=id), code=302)


@app.template_filter('date')
def timectime(timestamp):
    if timestamp is not None:
        return datetime.date(datetime.fromtimestamp(timestamp))
    else:
        return ""


@app.errorhandler(404)
def page_not_found(e):
    messages = get_flashed_messages(with_categories=True)
    return render_template('404.html', messages=messages), 404
