from unittest import TestCase
from unittest.mock import patch, Mock

from app.dlq.infrastructure.mq.exceptions.mq_exception import MqException
from app.dlq.infrastructure.mq.listeners.transfer_dlq_queue_listener import TransferDlqQueueListener
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


@patch(
    "app.dlq.infrastructure.mq.listeners.dlq_queue_listener_base.DlqQueueListenerBase"
    "._DlqQueueListenerBase__get_message_max_retries"
)
@patch(
    "app.dlq.infrastructure.mq.listeners.stomp_listener_base.StompListenerBase"
    "._StompListenerBase__create_subscribed_mq_connection"
)
class TestTransferDlqQueueListener(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_MESSAGE_MAX_RETRIES = 3

        cls.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED = {
            "test": "test",
            "admin_metadata": {
                "original_queue": "test_queue",
                "retry_count": 2
            }
        }

        cls.TEST_MESSAGE_BODY_MISSING_ADMIN_METADATA = {
            "test": "test"
        }

        cls.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED_MISSING_ORIGINAL_QUEUE = {
            "test": "test",
            "admin_metadata": {
                "retry_count": 2
            }
        }

        cls.TEST_MESSAGE_BODY_MISSING_RETRY_COUNT = {
            "test": "test",
            "admin_metadata": {
                "original_queue": "test_queue",
            }
        }

        cls.TEST_MESSAGE_BODY_MAX_RETRIES_REACHED = {
            "test": "test",
            "admin_metadata": {
                "original_queue": "test_queue",
                "retry_count": cls.TEST_MESSAGE_MAX_RETRIES
            }
        }

    def test_handle_received_message_max_retries_unreached_happy_path(
            self,
            create_subscribed_mq_connection_mock,
            get_mq_max_retries_mock
    ) -> None:
        get_mq_max_retries_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)

        sut = TransferDlqQueueListener(transfer_resubmitting_publisher=transfer_resubmitting_publisher_mock)
        sut._handle_received_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )

    def test_handle_received_message_max_retries_unreached_transfer_resubmitting_publisher_raises_mq_exception(
            self,
            create_subscribed_mq_connection_mock,
            get_mq_max_retries_mock
    ) -> None:
        get_mq_max_retries_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_stub = Mock(spec=TransferResubmittingPublisher)
        transfer_resubmitting_publisher_stub.resubmit_message.side_effect = MqException()

        sut = TransferDlqQueueListener(transfer_resubmitting_publisher=transfer_resubmitting_publisher_stub)

        with self.assertRaises(MqException):
            sut._handle_received_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED)

        transfer_resubmitting_publisher_stub.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )

    def test_handle_received_message_max_retries_unreached_missing_original_queue(
            self,
            create_subscribed_mq_connection_mock,
            get_mq_max_retries_mock
    ) -> None:
        get_mq_max_retries_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)

        sut = TransferDlqQueueListener(transfer_resubmitting_publisher=transfer_resubmitting_publisher_mock)
        sut._handle_received_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED_MISSING_ORIGINAL_QUEUE)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()

    def test_handle_received_message_missing_retry_count(
            self,
            create_subscribed_mq_connection_mock,
            get_mq_max_retries_mock
    ) -> None:
        get_mq_max_retries_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)

        sut = TransferDlqQueueListener(transfer_resubmitting_publisher=transfer_resubmitting_publisher_mock)
        sut._handle_received_message(self.TEST_MESSAGE_BODY_MISSING_RETRY_COUNT)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()

    def test_handle_received_message_max_retries_reached_happy_path(
            self,
            create_subscribed_mq_connection_mock,
            get_mq_max_retries_mock
    ) -> None:
        get_mq_max_retries_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)

        sut = TransferDlqQueueListener(transfer_resubmitting_publisher=transfer_resubmitting_publisher_mock)
        sut._handle_received_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_REACHED)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()
