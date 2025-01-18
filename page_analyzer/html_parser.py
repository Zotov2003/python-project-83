from bs4 import BeautifulSoup


def parse_page(response_text):
    html_data = BeautifulSoup(response_text, 'html.parser')
    title = html_data.title.string if html_data.title else None
    h1 = html_data.h1.string if html_data.h1 else None

    description = html_data.find('meta', {'name': 'description'})
    description_content = description.get('content') if description else None

    page_data = {
        'title': title,
        'h1': h1,
        'description': description_content
    }

    return page_data
