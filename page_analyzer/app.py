import os
import psycopg2
from validators.url import url
from urllib.parse import urlparse
from dotenv import load_dotenv, find_dotenv
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, get_flashed_messages)

app = Flask(__name__)

load_dotenv(find_dotenv())

app.secret_key = os.environ.get("SECRETKEY")

dbname = os.environ.get("DBNAME")
user = os.environ.get("USER")
password = os.environ.get("PASSWORD")
host = os.environ.get("HOST")
print("*****user******", user)
print("*****password******", password)
conn = psycopg2.connect(dbname=dbname,
                        user=user,
                        password=password,
                        host=host)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS urls")
cur.execute("CREATE TABLE urls( \
             id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, \
             name varchar(255) UNIQUE NOT NULL, \
             created_at timestamp)")


@app.route('/', methods=['GET'])
def start():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        address = urlparse(request.form.get('url'))
        scheme = address[0] if address[0] else 'http'
        scheme += '://'
        netloc = address[1]
        path = address[2]
        link = scheme + netloc + path
        if len(link) > 255 or not url(link):
            flash('Некорректный URL', 'danger')
            return redirect(url_for('start'), code=302)
        cur.execute("SELECT id FROM urls WHERE name = (%s)", (link,))
        records = cur.fetchall()
        if records:
            flash('Страница уже существует', 'info')
            return redirect(url_for('site', id=records[0][0]), code=302)
        cur.execute("SELECT CURRENT_TIMESTAMP")
        timestamp = cur.fetchall()
        cur.execute("SELECT MAX(id)+1 FROM urls")
        max_id = cur.fetchall()
        cur.execute("INSERT INTO urls \
                    (name, created_at) \
                    VALUES ((%s), (%s))",
                    (link, timestamp[0][0]))
        conn.commit()
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('site', id=max_id[0][0]), code=302)
    elif request.method == 'GET':
        cur.execute("SELECT id, name, created_at FROM urls ORDER BY id DESC")
        records = cur.fetchall()
        messages = get_flashed_messages(with_categories=True)
        return render_template('urls.html', messages=messages, rows=records)


@app.route('/urls/<id>', methods=['GET'])
def site(id):
    cur.execute("SELECT name FROM urls WHERE id = (%s)", (id,))
    records = cur.fetchall()

    if not records:
        flash('Такой страницы не существует', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('url_id.html',
                               messages=messages,
                               site_name='<error>')
    site_name = records[0][0]
    cur.execute("SELECT id, name, created_at FROM urls WHERE id = (%s)", (id,))
    records = cur.fetchall()

    messages = get_flashed_messages(with_categories=True)
    return render_template('url_id.html',
                           messages=messages,
                           site_name=site_name,
                           record=records[0])
