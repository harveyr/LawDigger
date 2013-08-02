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

    def title(self, version):
        version = str(version)
        if version in self.titles:
            return self.titles[version]
        return ''

    def text(self, version):
        return self.texts[str(version)]


class OregonRevisedStatute(Law):
    law_code = 'ors'
    serialize_attrs = ['state_code']

    def __str__(self):
        return '<ORS {subs} {versions}>'.format(
            subs=self.subsection,
            versions=self.texts.keys())

    @property
    def filename(self):
        return self.subsection

    def get_version(self, version):
        return '{subs}. {title}\n{text}'.format(
            subs=self.subsection,
            title=self.title(version),
            text=self.text(version))
