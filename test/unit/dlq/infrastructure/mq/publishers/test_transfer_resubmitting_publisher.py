from unittest import TestCase
from unittest.mock import patch

from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class TestTransferResubmittingPublisher(TestCase):

    @patch("app.dlq.infrastructure.mq.publishers.stomp_publisher_base.StompPublisherBase._publish_message")
    def test_publish_message_happy_path(self, parent_publish_message_mock) -> None:
        sut = TransferResubmittingPublisher()

        test_original_queue = "test_queue"
        test_current_retry_count = 2
        test_original_message_body = {
            "test": "test",
            "admin_metadata": {
                "original_queue": test_original_queue,
                "retry_count": test_current_retry_count
            }
        }

        sut.publish_message(
            original_message_body=test_original_message_body,
            current_retry_count=test_current_retry_count,
            queue_name=test_original_queue
        )

        expected_message_body = test_original_message_body
        expected_message_body["admin_metadata"]["retry_count"] = test_current_retry_count + 1
        expected_queue_name = test_original_queue
        parent_publish_message_mock.assert_called_once_with(
            expected_message_body,
            expected_queue_name
        )
