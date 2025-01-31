import requests
import os

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.db import DatabaseManager
from page_analyzer.helpers import fetch_url_data, parse_html_data
from page_analyzer.tasks import async_check_all_urls
from page_analyzer.url_parser import url_parser
from page_analyzer.url_validator import validate

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.get('/')
def page_analyzer():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    new_url = request.form.get('url')

    error = validate(new_url)
    if error:
        flash(error, 'danger')
        return render_template('index.html'), 422
    normal_url = url_parser(new_url)
    db_manager = DatabaseManager()
    url_data = db_manager.get_url_by_name(normal_url)
    if url_data:
        flash('Страница уже существует', 'primary')
        return redirect(url_for('show_url', id=url_data.id))
    else:
        new_url_data = db_manager.add_url_to_db(normal_url)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('show_url', id=new_url_data[0]))


@app.get('/urls')
def show_all_urls():
    db_manager = DatabaseManager()
    all_urls = db_manager.get_urls_with_latest_check()
    return render_template('urls.html', all_urls=all_urls)


@app.post('/urls/checks')
def check_all_urls():
    async_check_all_urls.delay()
    flash('Процесс проверки всех страниц запушен', 'success')

    return redirect(url_for('show_all_urls'))


@app.get('/urls/<int:id>')
def show_url(id):
    db_manager = DatabaseManager()
    url_data = db_manager.get_url_by_id(id)
    if not url_data:
        return render_template('404.html'), 404

    all_checks = db_manager.get_checks_desc(id)
    return render_template(
        'url.html',
        url_data=url_data,
        all_checks=all_checks
    )


@app.post('/urls/<int:id>/checks')
def add_check(id):
    db_manager = DatabaseManager()
    url = db_manager.get_url_by_id(id)
    if not url:
        return render_template('404.html'), 404

    try:
        status_code, html_content = fetch_url_data(url[0].name)
    except requests.exceptions.RequestException as e:
        error_message = f'Произошла ошибка при проверке: {e}'
        flash(error_message, 'danger')
        return redirect(url_for('show_url', id=id))

    if status_code != 200:
        error_message =\
            f'Произошла ошибка при проверке: статус ответа {status_code}'
        flash(error_message, 'danger')
        return redirect(url_for('show_url', id=id))

    page_data = parse_html_data(html_content)
    if 'error' in page_data:
        flash(page_data['error'], 'danger')

    db_manager.add_check_to_db(id, status_code, page_data)
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url', id=id))
