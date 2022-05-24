from unittest import TestCase
from unittest.mock import patch, Mock

from stomp import Connection

from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.domain.services.exceptions.dlq_service_exception import DlqServiceException
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

        cls.TEST_MESSAGE_SUBSCRIPTION = "test"

    def setUp(self) -> None:
        self.connection_mock = Mock(spec=Connection)

    def test_handle_received_message_happy_path(self, create_subscribed_mq_connection_mock) -> None:
        create_subscribed_mq_connection_mock.return_value = self.connection_mock
        dlq_service_mock = Mock(spec=DlqService)

        sut = TransferDlqQueueListener(dlq_service=dlq_service_mock)

        sut._handle_received_message(self.TEST_MESSAGE_BODY, self.TEST_MESSAGE_ID, self.TEST_MESSAGE_SUBSCRIPTION)

        dlq_service_mock.handle_dlq_message.assert_called_once_with(self.TEST_MESSAGE_BODY, self.TEST_MESSAGE_ID)
        self.connection_mock.ack.assert_called_once_with(
            id=self.TEST_MESSAGE_ID,
            subscription=self.TEST_MESSAGE_SUBSCRIPTION
        )

    def test_handle_received_service_raises_dlq_service_exception(self, create_subscribed_mq_connection_mock) -> None:
        create_subscribed_mq_connection_mock.return_value = self.connection_mock
        dlq_service_stub = Mock(spec=DlqService)
        dlq_service_stub.handle_dlq_message.side_effect = DlqServiceException("test", "test")

        sut = TransferDlqQueueListener(dlq_service=dlq_service_stub)

        sut._handle_received_message(self.TEST_MESSAGE_BODY, self.TEST_MESSAGE_ID, self.TEST_MESSAGE_SUBSCRIPTION)

        self.connection_mock.ack.assert_not_called()
