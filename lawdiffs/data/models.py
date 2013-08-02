import inspect
# from .client import client
import logging
import mongoengine as moe
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
    collection_name = 'or_ors'

    subsection = moe.StringField(unique=True, required=True)
    versions = moe.DictField(default={})
    state_code = moe.StringField()

    meta = {'allow_inheritance': True}

    @classmethod
    def class_serialize(cls, obj):
        return {
            'subsection': obj.subsection,
            'versions': obj.versions.keys(),
            'state_code': obj.state_code
        }

    @classmethod
    def fetch_by_state_code(cls, state_code):
        c = cls.collection()
        return c.find({'state_code': state_code})

    def init_version(self, version):
        version = str(version)
        if not version in self.versions:
            self.versions[version] = {
                'text': ''
            }
        self.save()

    def get_version_value(self, version, key):
        version = str(version)
        return self.versions[version][key]

    def _update_version(self, version, key, value):
        version = str(version)
        self.versions[version][key] = value
        self.save()

    def set_version_title(self, version, title):
        self._update_version(version, 'title', title)

    def append_version_text(self, version, text):
        new_text = self.get_version_value(version, 'text') + text
        self._update_version(version, 'text', new_text)


class OregonRevisedStatute(Law):
    state_code = 'or'
    serialize_attrs = ['state_code']

    def __str__(self):
        return '<ORS {subs} [{versions}]>'.format(
            subs=self.subsection,
            versions=self.versions.keys())

    @property
    def filename(self):
        return self.subsection

    def get_version(self, version):
        version = self.versions[str(version)]
        return '{subs}. {title}\n{text}'.format(
            subs=self.subsection,
            title=version['title'],
            text=version['text'])
