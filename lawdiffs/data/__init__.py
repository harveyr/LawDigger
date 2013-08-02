import logging
import datetime
import calendar
import json
import pymongo
from bson.objectid import ObjectId
from werkzeug.contrib.cache import SimpleCache
logger = logging.getLogger(__name__)
import mongoengine as moe

from . import models


class LawDiffSerializer(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Serializeable):
            return o.serialize()
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
        elif isinstance(o, moe.queryset.QuerySet):
            return [obj for obj in o]


def jsonify(obj):
    return json.dumps(obj, cls=LawDiffSerializer)


def htmlify(text):
    html = ''
    for p in [p for p in text.split('\n\n') if p]:
        html += '<p>' + p + '</p>'
    return html


cache = SimpleCache()
