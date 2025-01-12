import requests

from page_analyzer.html_parser import parse_page


def fetch_url_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_text = response.text
    except requests.exceptions.RequestException as e:
        return 0, {'title': '', 'h1': '', 'description': f'Ошибка сети: {str(e)}'}

    page_data = parse_page(html_text)
    return response.status_code, page_data