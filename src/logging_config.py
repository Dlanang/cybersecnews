import logging

logging.basicConfig(
    level=logging.INFO,
    format='{"asctime": "%(asctime)s", "name": "%(name)s", "levelname": "%(levelname)s", "filename": "%(filename)s", "lineno": %(lineno)d, "message": "%(message)s"}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
