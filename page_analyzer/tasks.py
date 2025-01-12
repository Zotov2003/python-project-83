from page_analyzer.celery_config import celery_app
from page_analyzer.db import DatabaseRepository
from page_analyzer.helpers import fetch_url_data


@celery_app.task
def async_check_all_urls():
    repo = DatabaseRepository()
    all_urls = repo.get_urls_with_latest_check()
    for url in all_urls:
        status_code, page_data = fetch_url_data(url.name)
        repo.add_check_to_db(url.id, status_code, page_data)