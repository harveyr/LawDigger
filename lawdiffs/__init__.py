import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_formats = [
    '[%(levelname)s] %(message)s',
    '[%(levelname)s %(name)s:%(lineno)d] %(message)s',
    '[%(levelname)s %(name)s.%(funcName)s:%(lineno)d] %(message)s',
    '[%(levelname)s %(name)s.%(funcName)s:%(lineno)d]\n > %(message)s'
]

format = log_formats[3]
handler = logging.StreamHandler()
formatter = logging.Formatter(format)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
