"""
This module defines a DlqService, which is a domain service that defines DLQ operations.
"""

import os
from logging import Logger

from app.common.domain.mailing.exceptions.mailing_exception import MailingException
from app.common.domain.mailing.mailing_service import IMailingService
from app.common.domain.mq.exceptions.mq_exception import MqException
from app.dlq.domain.models.dlq_email_reason import DlqEmailReason
from app.dlq.domain.services.dlq_email_factory import DlqEmailFactory
from app.dlq.domain.services.exceptions.dlq_email_notification_exception import DlqEmailNotificationException
from app.dlq.domain.services.exceptions.dlq_message_missing_field_exception import DlqMessageMissingFieldException
from app.dlq.domain.services.exceptions.dlq_message_resubmitting_exception import DlqMessageResubmittingException
from app.dlq.infrastructure.mq.publishers.resubmitting_publisher_base import ResubmittingPublisherBase


class DlqService:
    __DEFAULT_MESSAGE_MAX_RETRIES = 3

    def __init__(
            self,
            resubmitting_publisher: ResubmittingPublisherBase,
            mailing_service: IMailingService,
            logger: Logger
    ) -> None:
        self.__resubmitting_publisher = resubmitting_publisher
        self.__mailing_service = mailing_service
        self.__logger = logger
        self.__dlq_email_factory = DlqEmailFactory()

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
            self.__send_missing_message_fields_email_notification(message_id)
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
                self.__logger.info("Error when resubmitting DLQ message with id {}...".format(message_id))
                self.__send_resubmit_error_email_notification(message_id)
                raise DlqMessageResubmittingException(message_id, str(me))

            self.__logger.info("Message {} resubmitted".format(message_id))
            self.__send_message_resubmitted_email_notification(message_id)
        else:
            self.__logger.info("Maximum message retry count reached for message {}".format(message_id))
            self.__send_max_retries_reached_email_notification(message_id)

    def __send_missing_message_fields_email_notification(self, message_id: str) -> None:
        self.__logger.info("Sending 'missing message required fields' notification email...")
        missing_message_required_fields_email = self.__dlq_email_factory.get_dlq_email(
            DlqEmailReason.MISSING_MESSAGE_REQUIRED_FIELDS,
            message_id
        )
        try:
            self.__mailing_service.send_email(missing_message_required_fields_email)
        except MailingException as me:
            self.__logger.error(str(me))
            raise DlqEmailNotificationException(message_id, str(me))

    def __send_resubmit_error_email_notification(self, message_id: str) -> None:
        self.__logger.info("Sending 'resubmit error' notification email...")
        resubmit_error_email = self.__dlq_email_factory.get_dlq_email(DlqEmailReason.RESUBMIT_ERROR, message_id)
        try:
            self.__mailing_service.send_email(resubmit_error_email)
        except MailingException as me:
            self.__logger.error(str(me))
            raise DlqEmailNotificationException(message_id, str(me))

    def __send_message_resubmitted_email_notification(self, message_id: str) -> None:
        self.__logger.info("Sending 'message resubmitted' notification email...")
        message_resubmitted_email = self.__dlq_email_factory.get_dlq_email(
            DlqEmailReason.MESSAGE_RESUBMITTED,
            message_id
        )
        try:
            self.__mailing_service.send_email(message_resubmitted_email)
        except MailingException as me:
            self.__logger.error(str(me))
            raise DlqEmailNotificationException(message_id, str(me))

    def __send_max_retries_reached_email_notification(self, message_id: str) -> None:
        self.__logger.info("Sending 'max retries reached' notification email...")
        max_retries_reached_email = self.__dlq_email_factory.get_dlq_email(
            DlqEmailReason.MAX_RETRIES_REACHED,
            message_id
        )
        try:
            self.__mailing_service.send_email(max_retries_reached_email)
        except MailingException as me:
            self.__logger.error(str(me))
            raise DlqEmailNotificationException(message_id, str(me))
