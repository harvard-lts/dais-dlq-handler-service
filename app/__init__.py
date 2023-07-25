import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, Response
from healthcheck import HealthCheck

from app.health.application.services.exceptions.get_current_commit_hash_exception import GetCurrentCommitHashException
from app.health.application.services.git_service import GitService

LOG_FILE_DEFAULT_PATH = "/home/hdhs/logs/hdhs.log"
LOG_FILE_DEFAULT_LEVEL = logging.DEBUG
LOG_FILE_BACKUP_COUNT = 1
LOG_ROTATION = "midnight"

APPLICATION_MAINTAINER = "Harvard Library Technology Services"
APPLICATION_GIT_REPOSITORY = "https://github.com/harvard-lts/hdc3a-dlq-handler-service"

logger = logging.getLogger()


def create_app() -> Flask:
    configure_logger()
    
    app = Flask(__name__)
    setup_health_check(app)
    disable_cached_responses(app)

    return app


def configure_logger() -> None:
    log_level = os.getenv('LOG_LEVEL', LOG_FILE_DEFAULT_LEVEL)
        
    log_file_path = os.getenv("LOG_FILE_PATH", LOG_FILE_DEFAULT_PATH)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when=LOG_ROTATION,
        backupCount=LOG_FILE_BACKUP_COUNT
    )
    logger = logging.getLogger('ddhs')
        
    logger.addHandler(file_handler)
    file_handler.setFormatter(formatter)
    logger.setLevel(log_level)


def setup_health_check(app: Flask) -> None:
    health_check = HealthCheck(success_ttl=None, failed_ttl=None)

    git_service = GitService()
    try:
        current_commit_hash = git_service.get_current_commit_hash()
    except GetCurrentCommitHashException as e:
        logger.error(str(e))
        raise e

    add_application_section_to_health_check(current_commit_hash, health_check)

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


def disable_cached_responses(app: Flask) -> None:
    @app.after_request
    def add_response_headers(response: Response) -> Response:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response
