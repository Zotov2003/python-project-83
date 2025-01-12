import os
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    render_template,
    request,
    url_for,
    get_flashed_messages,
    redirect
)
from urllib.parse import urlparse
from page_analyzer.db import DatabaseRepository
from page_analyzer.helpers import fetch_url_data
from page_analyzer.tasks import async_check_all_urls
from page_analyzer.url_validator import validate

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

repo = DatabaseRepository(os.getenv('DATABASE_URL'))

def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.get('/')
def page_analyzer():
    return render_template('index.html', flashed_messages=get_flashed_messages(with_categories=True))

@app.post('/urls')
def add_url():
    new_url = request.form.get('url')
    normalized_url = normalize_url(new_url)

    error = validate(new_url)
    if error:
        flash(error, 'danger')
        return render_template('index.html'), 422

    url_data = repo.add_url_to_db_with_returning(normalized_url)
    if url_data:
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('show_url', id=url_data.id))
    else:
        flash('Ошибка при добавлении страницы', 'danger')
        return redirect(url_for('page_analyzer'))

@app.get('/urls')
def show_all_urls():
    all_urls = repo.get_urls_with_latest_check()
    return render_template('urls.html', all_urls=all_urls, flashed_messages=get_flashed_messages(with_categories=True))

@app.post('/urls/checks')
def check_all_urls():
    async_check_all_urls.delay()
    flash('Процесс проверки всех страниц запушен', 'success')
    return redirect(url_for('show_all_urls'))

@app.get('/urls/<int:id>')
def show_url(id):
    url_data = repo.get_url_by_id(id)
    if not url_data:
        return render_template('404.html'), 404

    all_checks = repo.get_checks_desc(id)
    return render_template(
        'url.html',
        url_data=url_data,
        all_checks=all_checks,
        flashed_messages=get_flashed_messages(with_categories=True)
    )

@app.post('/urls/<id>/checks')
def add_check(id):
    url = repo.get_url_by_id(id)
    if not url:
        return render_template('404.html'), 404

    status_code, page_data = fetch_url_data(url[0].name)
    if status_code == 0:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        repo.add_check_to_db(id, status_code, page_data)
        flash('Страница успешно проверена', 'success')

    return redirect(url_for('show_url', id=id))
