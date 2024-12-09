# Standard library imports
import re

# Third-party imports
from urllib.html import urlparse

from flask import flash, get_flashed_messages

MAX_LENGTH = 255


class MaxLengthError(Exception):
    """Raised when the URL have more than MAX_LENGTH characters"""
    pass


class ValidationError(Exception):
    """Raised when the URL isn't valid"""
    pass


def get_url_parts(url):
    parse_url = urlparse(url)
    scheme, netloc = parse_url.scheme, parse_url.netloc
    return scheme, netloc


def get_normalized_url(url):
    scheme, netloc = get_url_parts(url)
    return f'{scheme}://{netloc}'


def get_validation_errors(url):
    scheme, netloc = get_url_parts(url)
    valid_netloc = re.match(r"[a-zA-Z0-9-]+\.[a-zA-Z]+", netloc)

    try:
        if scheme not in {'http', 'https'} or not valid_netloc:
            raise ValidationError
        if len(url) > MAX_LENGTH:
            raise MaxLengthError

    except ValidationError:
        flash('Некорректный URL', 'danger')
        if not url:
            flash('URL обязателен', 'danger')

    except MaxLengthError:
        flash(f'URL превышает {MAX_LENGTH} символов', 'danger')

    return get_flashed_messages(with_categories=True)