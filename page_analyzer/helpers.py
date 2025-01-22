import requests
from bs4 import BeautifulSoup


def fetch_url_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.status_code, response.text
    except requests.exceptions.Timeout as e:
        return 408, f'Таймаут запроса: {e}'
    except requests.exceptions.HTTPError as e:
        return e.response.status_code, f'HTTP ошибка {e.response.status_code}: {e.response.text}'
    except requests.exceptions.RequestException as e:
        return 500, f'Общая ошибка запроса: {e}'


def parse_html_data(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else ''
        h1 = soup.find('h1').string if soup.find('h1') else ''
        description = \
            soup.find('meta', attrs={'name': 'description'})['content'] \
            if soup.find('meta', attrs={'name': 'description'}) else ''
        return {'title': title, 'h1': h1, 'description': description}
    except AttributeError as e:
        return {'error': f'AttributeError during parsing: {e}'}
    except Exception as e:
        return {'error': f'An unexpected error occurred: {e}'}
