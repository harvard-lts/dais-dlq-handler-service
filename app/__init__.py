import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from healthcheck import HealthCheck

from app.dlq.infrastructure.mq.listeners.process_dlq_queue_listener import ProcessDlqQueueListener
from app.dlq.infrastructure.mq.listeners.transfer_dlq_queue_listener import TransferDlqQueueListener
from app.health.application.services.exceptions.get_current_commit_hash_exception import GetCurrentCommitHashException
from app.health.application.services.git_service import GitService
from app.health.infrastructure.compound_connectivity_service import CompoundConnectivityService

LOG_FILE_DEFAULT_PATH = "/home/hdhs/logs/hdhs.log"
LOG_FILE_DEFAULT_LEVEL = logging.DEBUG
LOG_FILE_MAX_SIZE_BYTES = 2 * 1024 * 1024
LOG_FILE_BACKUP_COUNT = 1

APPLICATION_MAINTAINER = "Harvard Library Technology Services"
APPLICATION_GIT_REPOSITORY = "https://github.com/harvard-lts/hdc3a-dlq-handler-service"

logger = logging.getLogger()


def create_app() -> Flask:
    setup_queue_listeners()

    app = Flask(__name__)
    setup_health_check(app)

    return app


def configure_logger() -> None:
    log_file_path = os.getenv('LOG_FILE_PATH', LOG_FILE_DEFAULT_PATH)

    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=LOG_FILE_MAX_SIZE_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT
    )
    logger.addHandler(file_handler)

    log_level = os.getenv('LOG_LEVEL', LOG_FILE_DEFAULT_LEVEL)
    logger.setLevel(log_level)


def setup_queue_listeners() -> None:
    ProcessDlqQueueListener()
    TransferDlqQueueListener()


def setup_health_check(app: Flask) -> None:
    health_check = HealthCheck(success_ttl=None, failed_ttl=None)

    git_service = GitService()
    try:
        current_commit_hash = git_service.get_current_commit_hash()
    except GetCurrentCommitHashException as e:
        logger.error(str(e))
        raise e

    add_application_section_to_health_check(current_commit_hash, health_check)

    connectivity_service = CompoundConnectivityService()
    connectivity_service.create_connectivity_check(health_check)

    app.add_url_rule("/health", "health", view_func=lambda: health_check.run())


def add_application_section_to_health_check(current_commit_hash: str, health_check: HealthCheck) -> None:
    health_check.add_section(
        "application",
        {
            "maintainer": APPLICATION_MAINTAINER,
            "git_repository": APPLICATION_GIT_REPOSITORY,
            "code_version": {
                "commit_hash": current_commit_hash,
            }
        }
    )
