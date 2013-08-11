import logging
import re

logger = logging.getLogger(__name__)

unicode_characters = {
    'em_dash': u'\u2014'.encode('utf8'),
    'en_dash': u'\u2013'.encode('utf8'),
    'curly_left_quote': u'\u201C'.encode('utf8'),
    'curly_right_quote': u'\u201D'.encode('utf8'),
    'prime': u'\u2032'.encode('utf8'),
    'section': u'\u00A7'.encode('utf8')
}

curly_left_quote_re = re.compile(u'\u201C'.encode('utf8'))
curly_right_quote_re = re.compile(u'\u201D'.encode('utf8'))
# apostrophe_re = re.compile(u'\u0027'.encode('utf8'))
# left_single_quot_re = re.compile(u'\u2018'.encode('utf8'))
acute_accent_re = re.compile(u'\u00B4'.encode('utf8'))
prime_re = re.compile(u'\u2032'.encode('utf8'))
section_symbol_re = re.compile(u'\u00A7'.encode('utf8'))


def utf8(text):
    text = curly_left_quote_re.sub('"', text)
    text = curly_right_quote_re.sub('"', text)
    text = prime_re.sub("'", text)
    text = section_symbol_re.sub(u'\u00A7', text)
    try:
        return text.encode('utf8')
    except UnicodeDecodeError:
        index = 0
        for char in text:
            try:
                char.encode('utf8')
                index += 1
            except UnicodeDecodeError as e:
                logger.error(
                    'Decode fail: "{}" at indx {} in text: {}'.format(
                        char, index, text[index - 3:index + 100]))
                raise e
