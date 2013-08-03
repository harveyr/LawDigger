import inspect
# from .client import client
import logging
import mongoengine as moe
import re

logger = logging.getLogger(__name__)


# class MongoDocument(object):

#     collection_name = None

#     @classmethod
#     def collection(self):
#         return client.collection(self.collection_name)

#     @classmethod
#     def get_or_create(cls, doc_dict):
#         c = cls.collection()
#         for key in cls.unique_keys:
#             result = c.find_one({key: doc_dict[key]})
#             if result:
#                 return (result, False)
#         inserted_id = c.insert(doc_dict)
#         inserted_doc = c.find_one({'_id': inserted_id})
#         return (inserted_doc, True)

#     def fetch_by_unique_keys(self):
#         return None


#     def save(self):
#         serialized = self.serialize()
#         doc, created = self.__class__.get_or_create(self.serialize())
#         if not created:
#             for key, val in serialized.items():
#                 doc[key] = val
#                 c = self.__class__.collection()
#                 c.save(doc)


class Serializeable(object):
    def serialize(self):
        d = {}
        for cls in inspect.getmro(self.__class__):
            try:
                class_dict = cls.class_serialize(self)
                d = dict(d.items() + class_dict.items())
            except AttributeError:
                pass
            else:
                pass
            finally:
                pass
        return d


class Law(moe.Document, Serializeable):
    subsection = moe.StringField(unique=True, required=True)
    titles = moe.DictField()
    texts = moe.DictField()
    state_code = moe.StringField()
    file_path = moe.StringField()

    meta = {'allow_inheritance': True}

    @classmethod
    def class_serialize(cls, obj):
        return {
            'id': str(obj.id),
            'subsection': obj.subsection,
            'titles': obj.titles,
            'state_code': obj.state_code
        }

    @classmethod
    def fetch_by_code_code(cls, state_code):
        c = cls.collection()
        return c.find({'state_code': state_code})

    def save_attr(self, attr):
        collection = self.__class__._get_collection()
        collection.update(
            {'_id': self.id},
            {'$set': {attr: getattr(self, attr)}}
        )

    def set_version_title(self, version, title):
        self.titles[str(version)] = title
        self.save_attr('titles')

    def set_version_text(self, version, text):
        self.texts[str(version)] = text
        self.save_attr('texts')

    @property
    def versions(self):
        return self.texts.keys()

    def title(self, version):
        version = str(version)
        if version in self.titles:
            return self.titles[version]
        return ''

    def text(self, version, formatted=False):
        text = self.texts[str(version)]
        if formatted:
            return self.format_text(text)
        return text

    def htmlify(self, text):
        """Not using this."""
        logger.debug('text: {v}'.format(v=text))
        html = ''
        for p in [p for p in text.split('\n\n') if p]:
            html += '<p>' + p + '</p>'
        return html


class OregonRevisedStatute(Law):
    law_code = 'ors'
    serialize_attrs = ['state_code']

    def __str__(self):
        return '<ORS {subs} {versions}>'.format(
            subs=self.subsection,
            versions=self.texts.keys())

    @classmethod
    def subsection_float_to_string(cls, subsection):
        return '{0:.3f}'.format(subsection)

    @property
    def filename(self):
        return self.subsection

    def get_version(self, version):
        return '{subs}. {title}\n{text}'.format(
            subs=self.subsection,
            title=self.title(version),
            text=self.text(version, formatted=True))

    def format_text(self, text):
        if not text:
            logger.error(self)
            logger.error('self.titles: {v}'.format(v=self.titles))
            logger.error('self.texts: {v}'.format(v=self.texts))
            raise Exception(
                '{} did not supply any text to format_text()'.format(self))

        formatted = ''
        int_li = re.compile(r'(\(\d+\))')
        parts = [p.strip() for p in int_li.split(text)]

        for i in range(len(parts)):
            part = parts[i]
            prev_part = parts[i-1]
            if int_li.match(part):
                if i > 0:
                    if prev_part.endswith(('.', ':')):
                        formatted += '\n\n'
                    else:
                        formatted += ' '
                formatted += part
            else:
                formatted += self._format_char_list_items(part)
            formatted = formatted.strip()
            if formatted.endswith(']'):
                idx = formatted.rfind('[')
                formatted = formatted[:idx] + '\n\n' + formatted[idx:]
        return formatted.strip()

    def _format_char_list_items(self, text):
        char_li = re.compile(r'(\([a-z+]\))')
        parts = [p.strip() for p in char_li.split(text)]
        if len(parts) == 1:
            return ' ' + parts[0]

        formatted = ''
        for p in parts:
            if char_li.match(p):
                formatted += '\n\t' + p
            else:
                formatted += ' ' + p
        return formatted


