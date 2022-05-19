from abc import ABC

from app.dlq.infrastructure.mq.publishers.stomp_publisher_base import StompPublisherBase


class ResubmittingPublisherBase(StompPublisherBase, ABC):

    def publish_message(self, original_message_body: dict, current_retry_count: int, queue_name: str) -> None:
        self._logger.info("Increasing message retry count...")
        original_message_body['admin_metadata']['retry_count'] = current_retry_count + 1
        self._logger.info("Publishing message with body {} to queue {}".format(str(original_message_body), queue_name))
        self._publish_message(original_message_body, queue_name)
