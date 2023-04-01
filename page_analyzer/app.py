import os
import secrets
from urllib.parse import urlparse
from flask import (Flask, render_template, request, redirect,
                   url_for, flash)

from page_analyzer.modules.urls import (get_list_sites, check_site,
                                        normalize_url, check_url,
                                        get_data_site, add_site)


app = Flask(__name__)
secret_key = os.getenv('SECRET_KEY')
app.secret_key = secret_key if secret_key else secrets.token_bytes(32)


@app.route('/', methods=['GET'])
def start():
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def sites():
    records = get_list_sites()
    return render_template('urls.html', rows=records), 200


@app.post('/urls')
def add():
    address = urlparse(request.form.get('url'))
    link = normalize_url(address)
    if not check_url(link):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    id = add_site(link)
    return redirect(url_for('site', id=id), code=302)


@app.route('/urls/<int:id>', methods=['GET'])
def site(id):
    record, checks = get_data_site(id)

    if not record:
        flash('Такой страницы не существует', 'danger')
        return render_template('404.html'), 404

    return render_template('url_id.html',
                           site_name=record.name,
                           id=id,
                           checks=checks,
                           record=record)


@app.post('/urls/<int:id>/checks')
def check(id):
    check_site(id)
    return redirect(url_for('site', id=id), code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
