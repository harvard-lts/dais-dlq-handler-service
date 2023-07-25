"""
This module defines a DlqService, which is a domain service that defines DLQ operations.
"""

import os
import logging

from app.common.domain.mailing.exceptions.mailing_exception import MailingException
from app.common.domain.mailing.mailing_service import IMailingService
from app.dlq.domain.models.dlq_email_reason import DlqEmailReason
from app.dlq.domain.services.dlq_email_factory import DlqEmailFactory
from app.dlq.domain.services.exceptions.dlq_email_notification_exception import DlqEmailNotificationException
from app.dlq.domain.services.exceptions.dlq_message_missing_field_exception import DlqMessageMissingFieldException


class DlqService:
    __DEFAULT_MESSAGE_MAX_RETRIES = 3

    def __init__(self) -> None:
        self.__mailing_service = SmtpMailingService()
        self.__logger = logging.getLogger('ddhs')

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
            self.__logger.info("Sending 'missing message required fields' notification email...")
            self.__send_dlq_email(DlqEmailReason.MISSING_MESSAGE_REQUIRED_FIELDS, message_id)
            raise DlqMessageMissingFieldException(message_id, str(e))

        self.__logger.info("Received message {} has {} retries".format(message_id, retry_count))
        max_retries = self.__get_message_max_retries()
        self.__logger.info("Message max retries permitted: {}".format(max_retries))

        if retry_count < max_retries:
            self.__logger.info("Message {} resubmitted".format(message_id))
            self.__logger.info("Sending 'message resubmitted' notification email...")
            self.__send_dlq_email(DlqEmailReason.MESSAGE_RESUBMITTED, message_id)
        else:
            self.__logger.info("Maximum message retry count reached for message {}".format(message_id))
            self.__logger.info("Sending 'max retries reached' notification email...")
            self.__send_dlq_email(DlqEmailReason.MAX_RETRIES_REACHED, message_id)

    def __get_message_max_retries(self) -> int:
        return int(os.getenv('MESSAGE_MAX_RETRIES', self.__DEFAULT_MESSAGE_MAX_RETRIES))

    def __send_dlq_email(self, dlq_email_reason: DlqEmailReason, message_id: str) -> None:
        dlq_email_factory = DlqEmailFactory()
        dlq_email = dlq_email_factory.get_dlq_email(
            dlq_email_reason,
            message_id
        )
        try:
            self.__mailing_service.send_email(dlq_email)
        except MailingException as me:
            self.__logger.error(str(me))
            raise DlqEmailNotificationException(message_id, str(me))
