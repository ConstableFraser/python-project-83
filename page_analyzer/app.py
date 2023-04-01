import os
import secrets
from urllib.parse import urlparse
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, get_flashed_messages)

from page_analyzer.modules.urls import (get_list_sites, check_site,
                                        normalize_url, check_url,
                                        get_data_site, add_site,
                                        check_exist)


app = Flask(__name__)
secret_key = os.getenv('SECRET_KEY')
app.secret_key = secret_key if secret_key else secrets.token_bytes(32)


@app.route('/')
def start():
    return render_template('index.html')


@app.route('/urls')
def sites():
    records = get_list_sites()
    return render_template('urls.html', rows=records), 200


@app.post('/urls')
def add():
    address = urlparse(request.form.get('url'))
    link = normalize_url(address)
    if not check_url(link):
        flash('Некорректный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages), 422

    id = check_exist(link)
    if id:
        flash('Страница уже существует', 'info')
        return redirect(url_for('url', id=id), code=302)

    id = add_site(link)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url', id=id), code=302)


@app.route('/urls/<int:id>')
def url(id):
    record, checks = get_data_site(id)

    if not record:
        flash('Такой страницы не существует', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('404.html', messages=messages)

    messages = get_flashed_messages(with_categories=True)
    return render_template('url_id.html',
                           record=record,
                           checks=checks,
                           messages=messages)


@app.post('/urls/<int:id>/checks')
def check(id):
    if check_site(id):
        flash('Страница успешно проверена', 'success')
    else:
        flash('Произошла ошибка про проверке', 'danger')

    return redirect(url_for('url', id=id), code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
