from bs4 import BeautifulSoup


def get_page_data(content):
    soup = BeautifulSoup(content, 'html.parser')
    description = ''

    h1 = soup.h1.string if soup.h1 else ''

    title = soup.title.string if soup.title else ''

    dct = {'name': 'description'}
    description = soup.find(attrs=dct)
    description = description.get('content') if description else ''

    return {"h1": h1, "title": title, "description": description}
