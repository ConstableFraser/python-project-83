from bs4 import BeautifulSoup


def get_value(text, value):
    soup = BeautifulSoup(text, 'html.parser')

    if value == 'h1':
        return soup.h1.string if soup.h1 else ""

    elif value == 'title':
        return soup.title.string if soup.title else ""

    elif value == 'content':
        for item in soup.find_all(attrs={'name': 'description'}):
            if item.get('content'):
                return item.get('content')
        return ""

    else:
        return ""
