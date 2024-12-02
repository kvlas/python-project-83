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
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme or 'http'
    netloc = parsed_url.netloc or parsed_url.path
    return f'{scheme}://{netloc}'

def check_errors(url):
    if not url:
        flash('URL обязателен', 'danger')
        return get_flashed_messages(with_categories=True)

    if len(url) > MAX_LENGTH:
        flash(f'URL превышает {MAX_LENGTH} символов', 'danger')
        return get_flashed_messages(with_categories=True)

    parsed_url = urlparse(url)
    
    if parsed_url.scheme not in ('http', 'https'):
        flash('Некорректный URL', 'danger')
        return get_flashed_messages(with_categories=True)
    
    if not parsed_url.netloc:
        flash('Некорректный URL', 'danger')
        return get_flashed_messages(with_categories=True)
    
    try:
        netloc_idna = parsed_url.netloc.encode('idna').decode('ascii')
    except UnicodeError:
        flash('Некорректный URL', 'danger')
        return get_flashed_messages(with_categories=True)
    
    netloc_regex = re.compile(
        r'^(?:'
        r'[a-zA-Z0-9\-\.]+'
        r'|(?:\[[0-9a-fA-F:]+\])'
        r'|(?:\d{1,3}(?:\.\d{1,3}){3})'
        r')(?::\d+)?$'
    )
    
    if not netloc_regex.match(netloc_idna):
        flash('Некорректный URL', 'danger')
        return get_flashed_messages(with_categories=True)
    
    host, sep, port = netloc_idna.partition(':')
    if port:
        try:
            port_num = int(port)
            if not (0 < port_num < 65536):
                flash('Некорректный URL', 'danger')
                return get_flashed_messages(with_categories=True)
        except ValueError:
            flash('Некорректный URL', 'danger')
            return get_flashed_messages(with_categories=True)

    return []