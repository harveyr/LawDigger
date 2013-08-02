import logging
import inspect
import datetime
import calendar
import json
import pymongo
from bson.objectid import ObjectId
logger = logging.getLogger(__name__)

from . import models


class LawDiffSerializer(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)

        elif isinstance(o, datetime.datetime):
            # Trying UTC times so we can consistently compare age in any timezone
            # and do updates to single log entries on front end without having
            # to refresh entire log in order to get updated times for sorting.

            obj_date = calendar.timegm(o.timetuple()) * 1000 + o.microsecond / 1000
            # now = timegm(datetime.utcnow().timetuple() )
            # now = time.mktime(datetime.datetime.now().timetuple())
            # dt = time.mktime(o.timetuple())
            # return now - obj_date
            return obj_date
        elif isinstance(o, pymongo.cursor.Cursor):
            return [obj for obj in o]


def jsonify(obj):
    return json.dumps(obj, cls=LawDiffSerializer)


for name, obj in inspect.getmembers(models, inspect.isclass):
    if issubclass(obj, models.MongoDocument):
        pass

