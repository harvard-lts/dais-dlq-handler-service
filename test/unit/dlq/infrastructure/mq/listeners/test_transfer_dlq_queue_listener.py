from unittest import TestCase
from unittest.mock import patch, Mock

from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.infrastructure.mq.listeners.transfer_dlq_queue_listener import TransferDlqQueueListener


@patch(
    "app.dlq.infrastructure.mq.listeners.stomp_listener_base.StompListenerBase"
    "._StompListenerBase__create_subscribed_mq_connection"
)
class TestTransferDlqQueueListener(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_MESSAGE_BODY = {
            "test": "test",
            "admin_metadata": {
                "original_queue": "test_queue",
                "retry_count": 2
            }
        }

        cls.TEST_MESSAGE_ID = "test"

    def test_handle_received_message_happy_path(self, create_subscribed_mq_connection_mock) -> None:
        dlq_service_mock = Mock(spec=DlqService)

        sut = TransferDlqQueueListener(dlq_service=dlq_service_mock)
        sut._handle_received_message(self.TEST_MESSAGE_BODY, self.TEST_MESSAGE_ID)

        dlq_service_mock.handle_dlq_message.assert_called_once_with(self.TEST_MESSAGE_BODY, self.TEST_MESSAGE_ID)
