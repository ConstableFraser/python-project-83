from bs4 import BeautifulSoup


def get_page_contents(text, *args):
    soup = BeautifulSoup(text, 'html.parser')

    if args.count('h1'):
        h1 = soup.h1.string if soup.h1 else None

    if args.count('title'):
        title = soup.title.string if soup.title else None

    if args.count('content'):
        dct = {'name': 'description'}
        array = [x for x in soup.find_all(attrs=dct) if x.get('content')]
        description = array[0].get('content') if len(array) else None

    return h1, title, description
