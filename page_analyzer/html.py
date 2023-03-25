from bs4 import BeautifulSoup


def get_page_contents(text, value):
    soup = BeautifulSoup(text, 'html.parser')

    if value == 'h1':
        return soup.h1.string if soup.h1 else ""

    if value == 'title':
        return soup.title.string if soup.title else ""

    if value == 'content':
        dct = {'name': 'description'}
        array = [x for x in soup.find_all(attrs=dct) if x.get('content')]
        return array[0].get('content') if len(array) else ""

    return None
