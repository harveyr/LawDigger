import inspect
from .client import client
import logging
logger = logging.getLogger(__name__)


class MongoDocument(object):

    collection_name = None

    @classmethod
    def collection(self):
        return client.collection(self.collection_name)

    @classmethod
    def get_or_create(cls, doc_dict):
        c = cls.collection()
        for key in cls.unique_keys:
            result = c.find_one({key: doc_dict[key]})
            if result:
                return (result, False)
        inserted_id = c.insert(doc_dict)
        inserted_doc = c.find_one({'_id': inserted_id})
        return (inserted_doc, True)

    def fetch_by_unique_keys(self):
        return None

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

    def save(self):
        serialized = self.serialize()
        doc, created = self.__class__.get_or_create(self.serialize())
        if not created:
            for key, val in serialized.items():
                doc[key] = val
                c = self.__class__.collection()
                c.save(doc)


class Law(MongoDocument):
    collection_name = 'or_ors'
    unique_keys = ['subsection']

    @classmethod
    def class_serialize(cls, obj):
        return {
            'subsection': obj.subsection,
            'versions': obj.versions.keys()
        }

    def __init__(self, subsection):
        self.subsection = subsection
        self.versions = {}

    def _ensure_version(self, version):
        if not version in self.versions:
            self.versions[version] = {
                'text': ''
            }

    def _update_version(self, version, key, value):
        self._ensure_version(version)
        self.versions[version][key] = value

    def set_version_title(self, version, title):
        self._update_version(version, 'title', title)

    def append_version_text(self, version, text):
        self._ensure_version(version)
        new_text = self.versions[version]['text'] + text
        self._update_version(version, 'text', new_text)


class OregonRevisedStatute(Law):
    state_code = 'or'
    serialize_attrs = ['state_code']

    def __str__(self):
        return 'ORS {subs}'.format(subs=self.subsection)

    @property
    def filename(self):
        return self.subsection

    @property
    def full_law(self):
        return '{subs}. {title}\n{text}'.format(
            subs=self.subsection,
            title=self.title,
            text=self.text)

