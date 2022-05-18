from unittest import TestCase
from unittest.mock import patch

from app import TransferDlqQueueListener


@patch(
    "app.dlq.infrastructure.mq.listeners.stomp_listener_base.StompListenerBase"
    "._StompListenerBase__create_subscribed_mq_connection"
)
class TestTransferDlqQueueListener(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_MESSAGE = {
            "test": "test"
        }

    def test_handle_received_message_successful_happy_path(self, create_subscribed_mq_connection_mock) -> None:
        sut = TransferDlqQueueListener()
        sut._handle_received_message(self.TEST_MESSAGE)
