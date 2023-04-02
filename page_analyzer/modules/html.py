from bs4 import BeautifulSoup


def get_page_contents(text):
    soup = BeautifulSoup(text, 'html.parser')
    description = ''

    h1 = soup.h1.string if soup.h1 else ''

    title = soup.title.string if soup.title else ''

    dct = {'name': 'description'}
    array = [x for x in soup.find_all(attrs=dct) if x.get('content')]
    description = array[0].get('content') if len(array) else ''

    return {"h1": h1, "title": title, "description": description}
