import bs4
from ..data.encoder import unicode_chars

def soup_text(soup_elem):
    try:
        # text = soup_elem.get_text(',,,', strip=True).decode('utf-8')
        # text = self.newline_re.sub(" ", text)
        # text = re.sub(r',,,', '\n', text)
        text = soup_elem.get_text('\n', strip=True).encode('utf8')

        return text
    except AttributeError:
        if isinstance(soup_elem, bs4.element.NavigableString):
            return unicode(soup_elem)
        else:
            raise Exception('Unhandled type: {}'.format(
                type(soup_elem)))


def html_to_text(html):
    soup = bs4.BeautifulSoup(html)
    return soup_text(soup)
