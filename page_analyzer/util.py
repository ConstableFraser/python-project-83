from urllib.parse import urlparse
from validators.url import url as url_validator

MAX_LENGTH = 255


def is_valid_url(link):
    if len(link) > MAX_LENGTH or not url_validator(link):
        return False
    return True


def normalize_url(data):
    address = urlparse(data)
    scheme = address[0] if address[0] else 'http'
    scheme += '://'
    netloc = address[1]
    path = address[2]
    url = scheme + netloc + path
    return url
