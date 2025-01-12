from bs4 import BeautifulSoup


def parse_page(response_text):
    html_data = BeautifulSoup(response_text, 'html.parser')

    page_data = {}

    page_data['title'] = html_data.title.string if html_data.title else None

    page_data['h1'] = html_data.h1.string if html_data.h1 else None

    description = html_data.find('meta', {'name': 'description'})
    if description:
        page_data['description'] = description.get('content')

    return page_data