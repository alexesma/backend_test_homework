import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    filename='program.log',
    filemode='a'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class InvalidEnvs(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        logger.critical(message)


class InvalidDict(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class EmptyListError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        logger.error(message)


class InvalidStatus(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        logger.error(message)


class InvalidMessage(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        logger.error(message)
