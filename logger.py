import logging
from .config import settings

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_logger(name: str):
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL), format=LOG_FORMAT)
    return logging.getLogger(name)
