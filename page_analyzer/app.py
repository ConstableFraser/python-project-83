import os
import requests
from flask import (Flask, render_template, request,
                   redirect, url_for, flash)

from page_analyzer import util
from page_analyzer.database import urls, checks
from page_analyzer.html import get_page_contents


MAX_LENGTH = 255

app = Flask(__name__)
secret_key = os.getenv('SECRET_KEY', b'_5#y$$"F4f8z\n\xec]/')
app.secret_key = secret_key


@app.route('/')
def start():
    return render_template('index.html')


@app.route('/urls')
def sites():
    records = urls.get_urls_list()
    return render_template('urls.html', rows=records), 200


@app.post('/urls')
def add():
    user_url = request.form.get('url')

    if not util.is_valid_url(user_url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    valid_url = util.normalize_url(user_url)

    id = urls.get_id_url_by_name(valid_url)
    if id:
        flash('Страница уже существует', 'info')
        return redirect(url_for('url', id=id), code=302)

    id = urls.add_new_url(valid_url)
    flash('Страница успешно добавлена', 'success')

    return redirect(url_for('url', id=id), code=302)


@app.route('/urls/<int:id>')
def url(id):
    if not urls.get_name_url_by_id(id):
        flash('Такой страницы не существует', 'danger')
        return render_template('404.html')

    record = urls.get_url_info_by_id(id)
    check_list = checks.get_checks_list_by_id(id)
    return render_template('url_id.html',
                           record=record,
                           checks=check_list)


@app.post('/urls/<int:id>/checks')
def check(id):
    url_name = urls.get_name_url_by_id(id)
    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'My User Agent 1.0'})

    try:
        response = requests.get(*url_name, headers=headers)
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url', id=id), code=302)

    status_code = response.status_code
    tags = get_page_contents(response.text)
    checks.add_new_check(id, status_code, tags)

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url', id=id), code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
