"""
This module defines a DlqService, which is a domain service that defines DLQ operations.
"""

import os
from logging import Logger

from app.common.domain.mq.exceptions.mq_exception import MqException
from app.dlq.domain.services.exceptions.dlq_message_missing_field_exception import DlqMessageMissingFieldException
from app.dlq.domain.services.exceptions.dlq_message_resubmitting_exception import DlqMessageResubmittingException
from app.dlq.infrastructure.mq.publishers.resubmitting_publisher_base import ResubmittingPublisherBase


class DlqService:
    __DEFAULT_MESSAGE_MAX_RETRIES = 3

    def __init__(
            self,
            resubmitting_publisher: ResubmittingPublisherBase,
            logger: Logger
    ) -> None:
        self.__resubmitting_publisher = resubmitting_publisher
        self.__logger = logger

    def handle_dlq_message(self, message_body: dict, message_id: str) -> None:
        """
        Handles a DLQ message.

        :param message_body: message body
        :type message_body: dict
        :param message_id: message id
        :type message_id: str

        :raises DlqServiceException
        """
        try:
            message_admin_metadata = message_body['admin_metadata']
            original_queue = message_admin_metadata['original_queue']
            retry_count = int(message_admin_metadata['retry_count'])
        except KeyError as e:
            raise DlqMessageMissingFieldException(message_id, str(e))

        self.__logger.info("Received message {} has {} retries".format(message_id, retry_count))
        max_retries = int(os.getenv('MESSAGE_MAX_RETRIES', self.__DEFAULT_MESSAGE_MAX_RETRIES))
        self.__logger.info("Max retries permitted: {}".format(max_retries))

        if retry_count < max_retries:
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
