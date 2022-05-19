from unittest import TestCase
from unittest.mock import patch

from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class TestTransferResubmittingPublisher(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_ORIGINAL_QUEUE = "test_queue"
        cls.TEST_CURRENT_RETRY_COUNT = 2
        cls.TEST_ORIGINAL_MESSAGE_BODY = {
            "test": "test",
            "admin_metadata": {
                "original_queue": cls.TEST_ORIGINAL_QUEUE,
                "retry_count": cls.TEST_CURRENT_RETRY_COUNT
            }
        }

    @patch("app.dlq.infrastructure.mq.publishers.stomp_publisher_base.StompPublisherBase._publish_message")
    def test_publish_message_happy_path(self, parent_publish_message_mock) -> None:
        sut = TransferResubmittingPublisher()

        sut.publish_message(
            original_message_body=self.TEST_ORIGINAL_MESSAGE_BODY,
            current_retry_count=self.TEST_CURRENT_RETRY_COUNT,
            queue_name=self.TEST_ORIGINAL_QUEUE
        )

        expected_message_body = self.TEST_ORIGINAL_MESSAGE_BODY
        expected_message_body["admin_metadata"]["retry_count"] = self.TEST_CURRENT_RETRY_COUNT + 1
        expected_queue_name = self.TEST_ORIGINAL_QUEUE
        parent_publish_message_mock.assert_called_once_with(
            expected_message_body,
            expected_queue_name
        )
