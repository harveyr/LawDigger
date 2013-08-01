import inspect
from . import client
import logging
logger = logging.getLogger(__name__)


class MongoDocument(object):

    collection = None

    @classmethod
    def fetch():
        pass

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
            # except Exception, e:
            #     raise
            # else:
            #     pass
            # finally:
            #     pass
            # if hasattr(cls, 'serialize_attrs'):
            #     attrs += cls.serialize_attrs
            # else:
            #     break
        # if not attrs:
        #     raise Exception('{} has no serialize_attrs'.format(
        #         self.__class__.__name__))

        # return {key: getattr(self, key) for key in attrs}
        return d

    def insert(self):
        client.insert(self)


class Law(MongoDocument):
    collection = 'laws'
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

