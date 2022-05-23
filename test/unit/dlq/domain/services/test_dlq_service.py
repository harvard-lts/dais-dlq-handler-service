from logging import Logger
from unittest import TestCase
from unittest.mock import patch, Mock

from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.infrastructure.mq.exceptions.mq_exception import MqException
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


@patch("app.dlq.domain.services.dlq_service.os.getenv")
class TestDlqService(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_MESSAGE_MAX_RETRIES = 3

        cls.TEST_MESSAGE_BODY_MAX_RETRIES_REACHED = {
            "test": "test",
            "admin_metadata": {
                "original_queue": "test_queue",
                "retry_count": cls.TEST_MESSAGE_MAX_RETRIES
            }
        }

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

        cls.TEST_MESSAGE_ID = "test"

    def test_handle_dlq_message_max_retries_unreached_happy_path(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)

        sut = DlqService(resubmitting_publisher=transfer_resubmitting_publisher_mock, logger=Mock(spec=Logger))
        sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )

    def test_handle_dlq_message_max_retries_reached_happy_path(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)

        sut = DlqService(resubmitting_publisher=transfer_resubmitting_publisher_mock, logger=Mock(spec=Logger))
        sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_REACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()

    def test_handle_dlq_message_max_retries_unreached_transfer_resubmitting_publisher_raises_mq_exception(
            self,
            os_getenv_mock
    ) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_stub = Mock(spec=TransferResubmittingPublisher)
        transfer_resubmitting_publisher_stub.resubmit_message.side_effect = MqException()

        sut = DlqService(resubmitting_publisher=transfer_resubmitting_publisher_stub, logger=Mock(spec=Logger))

        with self.assertRaises(MqException):
            sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_stub.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )

    def test_handle_dlq_message_max_retries_unreached_missing_admin_metadata(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)

        sut = DlqService(resubmitting_publisher=transfer_resubmitting_publisher_mock, logger=Mock(spec=Logger))
        sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MISSING_ADMIN_METADATA, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()
