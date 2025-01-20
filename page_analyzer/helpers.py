import requests


def fetch_url_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return 0, f'Ошибка сети: {e}'


def parse_html_data(html_content):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else ''
        h1 = soup.find('h1').string if soup.find('h1') else ''
        description = soup.find('meta', attrs={'name': 'description'})[
            'content'] \
            if soup.find('meta', attrs={'name': 'description'}) else ''
        return {'title': title, 'h1': h1, 'description': description}
    except AttributeError as e:
        return \
            {'title': '', 'h1': '', 'description': f'Ошибка парсинга HTML: {e}'}
    except Exception as e:
        return {'title': '', 'h1': '',
                'description': f'Неизвестная ошибка при парсинге: {e}'}
