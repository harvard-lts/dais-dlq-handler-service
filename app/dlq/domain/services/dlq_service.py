import os
from logging import Logger

from app.dlq.domain.services.exceptions.dlq_message_missing_admin_metadata_exception import \
    DlqMessageMissingAdminMetadataException
from app.dlq.domain.services.exceptions.dlq_message_resubmitting_exception import DlqMessageResubmittingException
from app.dlq.infrastructure.mq.exceptions.mq_exception import MqException
from app.dlq.infrastructure.mq.publishers.resubmitting_publisher_base import ResubmittingPublisherBase


class DlqService:

    def __init__(
            self,
            resubmitting_publisher: ResubmittingPublisherBase,
            logger: Logger
    ) -> None:
        self.__resubmitting_publisher = resubmitting_publisher
        self.__logger = logger

    def handle_dlq_message(self, message_body: dict, message_id: str) -> None:
        message_admin_metadata = message_body.get('admin_metadata')
        if message_admin_metadata is None:
            self.__logger.error(
                "Received message {} does not include admin_metadata.".format(message_id)
            )
            raise DlqMessageMissingAdminMetadataException(message_id)

        retry_count = int(message_admin_metadata['retry_count'])
        self.__logger.info("Received message {} has {} retries".format(message_id, retry_count))
        max_retries = int(os.getenv('MESSAGE_MAX_RETRIES'))
        self.__logger.info("Max retries permitted: {}".format(max_retries))

        if retry_count < max_retries:
            original_queue = message_admin_metadata['original_queue']
            self.__logger.info("Resubmitting message {}...".format(message_id))
            try:
                self.__resubmitting_publisher.resubmit_message(
                    original_message_body=message_body,
                    current_retry_count=retry_count,
                    queue_name=original_queue
                )
            except MqException as me:
                self.__logger.error(str(me))
                raise DlqMessageResubmittingException(message_id, str(me))

            self.__logger.info("Message {} resubmitted".format(message_id))
            self.__logger.info("Sending notification message...")
            # TODO: notification message
        else:
            self.__logger.info("Maximum message retry count reached for message {}".format(message_id))
            self.__logger.info("Sending notification message...")
            # TODO: notification message
