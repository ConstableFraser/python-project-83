from validators.url import url

MAX_LENGTH = 255


def check_url(link):
    if len(link) > MAX_LENGTH or not url(link):
        return False
    return True


def normalize_url(address):
    scheme = address[0] if address[0] else 'http'
    scheme += '://'
    netloc = address[1]
    path = address[2]
    return scheme + netloc + path
