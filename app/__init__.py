import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask

from app.dlq.infrastructure.mq.listeners.transfer_dlq_queue_listener import TransferDlqQueueListener

LOG_FILE_DEFAULT_PATH = "/home/hdhs/logs/hdhs.log"
LOG_FILE_DEFAULT_LEVEL = logging.DEBUG
LOG_FILE_MAX_SIZE_BYTES = 2 * 1024 * 1024
LOG_FILE_BACKUP_COUNT = 1


def create_app(config_name: str = 'default') -> Flask:
    if config_name != 'testing':
        configure_logger()

    setup_queue_listeners()

    app = Flask(__name__)
    return app


def configure_logger() -> None:
    log_file_path = os.getenv('LOG_FILE_PATH', LOG_FILE_DEFAULT_PATH)
    logger = logging.getLogger()

    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=LOG_FILE_MAX_SIZE_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT
    )
    logger.addHandler(file_handler)

    log_level = os.getenv('LOG_LEVEL', LOG_FILE_DEFAULT_LEVEL)
    logger.setLevel(log_level)


def setup_queue_listeners() -> None:
    TransferDlqQueueListener()
