"""
This module defines a ResubmittingPublisherBase, which is an abstract class intended
to define common behavior for stomp-implemented resubmitting MQ publishers.
"""

from abc import ABC

from app.dlq.infrastructure.mq.publishers.stomp_publisher_base import StompPublisherBase


class ResubmittingPublisherBase(StompPublisherBase, ABC):

    def resubmit_message(self, original_message_body: dict, current_retry_count: int, queue_name: str) -> None:
        """
        Resubmits a message to a queue.

        :param original_message_body: original body of the message to resubmit
        :type original_message_body: dict
        :param current_retry_count: current retry count of the message to resubmit
        :type current_retry_count: int
        :param queue_name: queue name to resubmit the message
        :type queue_name: str

        :raises MqException
        """
        self._logger.info("Increasing message retry count...")
        original_message_body['admin_metadata']['retry_count'] = current_retry_count + 1
        self._logger.info("Publishing message with body {} to queue {}".format(str(original_message_body), queue_name))
        self._publish_message(original_message_body, queue_name)
