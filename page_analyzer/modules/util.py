from validators.url import url as url_validator

MAX_LENGTH = 255


def is_valid_url(link):
    if len(link) > MAX_LENGTH or not url_validator(link):
        return False
    return True


def build_url(address):
    scheme = address[0] if address[0] else 'http'
    scheme += '://'
    netloc = address[1]
    path = address[2]
    link = scheme + netloc + path
    return link if is_valid_url(link) else None
