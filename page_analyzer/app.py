from page_analyzer.validator import get_validation_errors, get_normalized_url
from page_analyzer.parser import get_response, get_parse_data
from page_analyzer.db import (
    add_url_to_db, get_urls_from_db, get_data_from_id,
    get_url_from_db, add_url_check_to_db, connect,
)
from flask import (
    Flask, render_template, request, redirect,
    flash, get_flashed_messages, url_for, abort
)
from dotenv import load_dotenv
import datetime
import os


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
    conn = connect(app)
    urls = get_urls_from_db(conn)
    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    errors = get_validation_errors(url)

    if errors:
        return render_template(
            'index.html',
            errors=errors
        ), 422

    url = get_normalized_url(url)
    conn = connect(app)
    date = datetime.datetime.now()

    is_added, id = add_url_to_db(url, date, conn)

    if is_added:
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')

    return redirect(url_for('url_page', id=id))


@app.get('/urls/<int:id>')
def url_page(id):
    conn = connect(app)
    data, checks = get_url_from_db(id, conn)
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
    conn = connect(app)
    url = get_data_from_id(id, conn).name
    response = get_response(url)

    if response:
        data = get_parse_data(response)
        date = datetime.datetime.now()

        add_url_check_to_db(id, date, data, conn)
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