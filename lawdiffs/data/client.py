import pymongo


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


def insert(obj):
    if not hasattr(obj, 'collection'):
        raise Exception('{} has no collection'.format(obj))

    collection = client.collection(obj.collection)

    if hasattr(obj, 'unique_keys'):
        for key in obj.unique_keys:
            result = collection.find_one({key: getattr(obj, key)})
            if result:
                raise Exception(
                    'Object already exists with unique key {}: {}'.format(
                        key, result))

    serialized = obj.serialize()
    print('serialized: {v}'.format(v=serialized))
    collection.insert(obj.serialize())
