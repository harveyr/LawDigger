import logging
import inspect
logger = logging.getLogger(__name__)

from . import models

for name, obj in inspect.getmembers(models, inspect.isclass):
    if issubclass(obj, models.MongoDocument):
        pass
