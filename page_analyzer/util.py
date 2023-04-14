from urllib.parse import urlparse
from validators.url import url as url_validator

MAX_LENGTH = 255


def is_valid_url(link):
    if len(link) > MAX_LENGTH or not url_validator(link):
        return False
    return True


def normalize_url(data):
    parsed_url = urlparse(data)
    return parsed_url.scheme + "://" + parsed_url.netloc
