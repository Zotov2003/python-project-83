from urllib.parse import urlparse


def url_parser(new_url):
    parsed_url = urlparse(new_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"
