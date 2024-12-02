from flask import flash, get_flashed_messages
from urllib.parse import urlparse
import re


MAX_LENGTH = 255


class MaxLengthError(Exception):
    """Raised when the URL have more than MAX_LENGTH characters"""
    pass


class ValidationError(Exception):
    """Raised when the URL isn't valid"""
    pass


def check_url(url):
    if not urlparse(url).scheme:
        url = f'http://{url}'
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    return f'{parsed_url.scheme}://{netloc}'


def check_errors(url):
    messages = []

    if not url:
        messages.append(('danger', 'URL обязателен'))

    if len(url) > MAX_LENGTH:
        messages.append(('danger', f'URL превышает {MAX_LENGTH} символов'))

    if not urlparse(url).scheme:
        url = f'http://{url}'

    parsed_url = urlparse(url)

    if parsed_url.scheme not in ('http', 'https'):
        messages.append(('danger', 'Некорректный URL'))

    if not parsed_url.netloc:
        messages.append(('danger', 'Некорректный URL'))

    try:
        netloc_idna = parsed_url.netloc.encode('idna').decode('ascii')
    except UnicodeError:
        messages.append(('danger', 'Некорректный URL'))

    netloc_regex = re.compile(
        r'^(?:'
        r'[a-zA-Z0-9\-\.]+'
        r'|(?:\[[0-9a-fA-F:]+\])'
        r'|(?:\d{1,3}(?:\.\d{1,3}){3})'
        r')(?::\d+)?$'
    )

    if not netloc_regex.match(netloc_idna):
        messages.append(('danger', 'Некорректный URL'))

    if parsed_url.port:
        if not (0 < parsed_url.port < 65536):
            messages.append(('danger', 'Некорректный URL'))

    for category, msg in messages:
        flash(msg, category)

    return get_flashed_messages(with_categories=True) if messages else []