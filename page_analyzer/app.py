import os
import datetime

import page_analyzer.db
from flask import Flask, render_template, request, redirect, flash, get_flashed_messages, url_for, abort
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
app.config.update(
    SECRET_KEY=SECRET_KEY,
    DATABASE_URL=DATABASE_URL
)


@app.route('/')
def main_page():
    return render_template(
        'index.html'
    )


@app.get('/urls')
def urls_list():
    conn = page_analyzer.db.connect(app)
    urls = page_analyzer.db.get_urls(conn)
    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    errors = page_analyzer.db.get_validation_errors(url)

    if errors:
        return render_template(
            'index.html',
            errors=errors
        ), 422

    url = page_analyzer.db.get_normalized_url(url)
    conn = page_analyzer.db.connect(app)
    date = datetime.datetime.now()

    is_added, id = page_analyzer.db.add_url(url, date, conn)

    if is_added:
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')

    return redirect(url_for('url_page', id=id))


@app.get('/urls/<int:id>')
def url_page(id):
    conn = page_analyzer.db.connect(app)
    data, checks = page_analyzer.db.get_url(id, conn)
    if not data:
        return abort(404)

    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        messages=messages,
        data=data,
        checks=checks
    )


@app.post('/urls/<int:id>/checks')
def check(id):
    conn = page_analyzer.db.connect(app)
    url = page_analyzer.db.get_data_from_id(id, conn).name
    response = page_analyzer.db.get_response(url)

    if response:
        data = page_analyzer.db.get_parse_data(response)
        date = datetime.datetime.now()

        page_analyzer.db.add_url_check(id, date, data, conn)
        flash('Страница успешно проверена', 'success')
    else:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('url_page', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        '404.html'
    ), 404


@app.errorhandler(Exception)
def internal_server_error(error):
    return render_template(
        '500.html'
    ), 500