import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOGHANDLER = logging.StreamHandler()
LOGFORMATTER = logging.Formatter(
    '[%(name)s:%(lineno)d] - %(levelname)s - %(message)s')
LOGHANDLER.setFormatter(LOGFORMATTER)
LOGHANDLER.setLevel(logging.DEBUG)
logger.addHandler(LOGHANDLER)
