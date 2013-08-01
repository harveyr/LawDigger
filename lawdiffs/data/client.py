import pymongo
from bson.objectid import ObjectId


class DbClient(object):
    DATABASE = 'lawdiffs'
    _client = None
    _db = None

    def connect(self):
        self._client = pymongo.MongoClient()
        self._db = self._client[self.DATABASE]

    @property
    def db(self):
        if not self._db:
            self.connect()
        return self._db

    def collection(self, collection_name):
        db = self.db
        return db[collection_name]

client = DbClient()

