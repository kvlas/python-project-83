import requests
from bs4 import BeautifulSoup
from page_analyzer.validator import MAX_LENGTH


HIDE_CHARS = '...'


def get_valid_length_data(data):
    if data:
        if len(data) > MAX_LENGTH:
            optimal_length = MAX_LENGTH - len(HIDE_CHARS)
            data = data[:optimal_length] + HIDE_CHARS
    return data


def get_response(url):
    try:
        response = requests.get(url, timeout=10)
        status_code = response.status_code
        if status_code < 100 or status_code > 400:
            raise ConnectionError
    except (requests.exceptions.ConnectionError, ConnectionError):
        return None
    return response


def get_parse_data(response):
    parse_data = dict(h1=None, title=None, description=None)

    parse_data['status_code'] = response.status_code
    html = BeautifulSoup(response.content, 'html.parser')

    description = [
        tag.get('content') for tag in html.find_all('meta') if
        tag.get('name') == 'description'
    ]

    if html.h1:
        h1 = html.h1.string
        parse_data['h1'] = get_valid_length_data(h1)

    if html.title:
        title = html.title.string
        parse_data['title'] = get_valid_length_data(title)

    if description:
        description = description[0]
        parse_data['description'] = get_valid_length_data(description)

    return parse_data