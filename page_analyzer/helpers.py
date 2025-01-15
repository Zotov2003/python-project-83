import requestsimport requests

from page_analyzer.html_parser import parse_page


def fetch_url_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.status_code, parse_page(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Сетевая ошибка: {e}")
        return 0, {'title': '', 'h1': '', 'description': 'Ошибка сети'}

from page_analyzer.html_parser import parse_page


def fetch_url_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        page_data = parse_page(response.text)
        return response.status_code, page_data
    except requests.exceptions.RequestException:
        return 0, {'title': '', 'h1': '', 'description': 'Ошибка сети'}