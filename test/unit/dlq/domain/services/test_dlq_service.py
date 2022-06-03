from logging import Logger
from unittest import TestCase
from unittest.mock import patch, Mock

from app.common.domain.mailing.exceptions.mailing_exception import MailingException
from app.common.domain.mailing.mailing_service import IMailingService
from app.common.domain.mq.exceptions.mq_exception import MqException
from app.dlq.domain.models.dlq_email_message_max_retries_reached import DlqEmailMaxRetriesReached
from app.dlq.domain.models.dlq_email_message_resubmitted import DlqEmailMessageResubmitted
from app.dlq.domain.models.dlq_email_missing_message_required_fields import DlqEmailMissingMessageRequiredFields
from app.dlq.domain.models.dlq_email_resubmit_error import DlqEmailResubmitError
from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.domain.services.exceptions.dlq_email_notification_exception import DlqEmailNotificationException
from app.dlq.domain.services.exceptions.dlq_message_missing_field_exception import DlqMessageMissingFieldException
from app.dlq.domain.services.exceptions.dlq_message_resubmitting_exception import DlqMessageResubmittingException
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
        mailing_service_mock = Mock(spec=IMailingService)

        sut = DlqService(
            resubmitting_publisher=transfer_resubmitting_publisher_mock,
            mailing_service=mailing_service_mock,
            logger=Mock(spec=Logger)
        )
        sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )
        self.assertIsInstance(mailing_service_mock.send_email.call_args.args[0], DlqEmailMessageResubmitted)

    def test_handle_dlq_message_max_retries_unreached_mailing_service_raises_exception(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)
        mailing_service_stub = Mock(spec=IMailingService)
        mailing_service_stub.send_email.side_effect = MailingException()

        sut = DlqService(
            resubmitting_publisher=transfer_resubmitting_publisher_mock,
            mailing_service=mailing_service_stub,
            logger=Mock(spec=Logger)
        )
        with self.assertRaises(DlqEmailNotificationException):
            sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )
        self.assertIsInstance(mailing_service_stub.send_email.call_args.args[0], DlqEmailMessageResubmitted)

    def test_handle_dlq_message_max_retries_reached_happy_path(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)
        mailing_service_mock = Mock(spec=IMailingService)

        sut = DlqService(
            resubmitting_publisher=transfer_resubmitting_publisher_mock,
            mailing_service=mailing_service_mock,
            logger=Mock(spec=Logger)
        )
        sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_REACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()
        self.assertIsInstance(mailing_service_mock.send_email.call_args.args[0], DlqEmailMaxRetriesReached)

    def test_handle_dlq_message_max_retries_reached_mailing_service_raises_exception(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)
        mailing_service_stub = Mock(spec=IMailingService)
        mailing_service_stub.send_email.side_effect = MailingException()

        sut = DlqService(
            resubmitting_publisher=transfer_resubmitting_publisher_mock,
            mailing_service=mailing_service_stub,
            logger=Mock(spec=Logger)
        )
        with self.assertRaises(DlqEmailNotificationException):
            sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_REACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()
        self.assertIsInstance(mailing_service_stub.send_email.call_args.args[0], DlqEmailMaxRetriesReached)

    def test_handle_dlq_message_max_retries_unreached_publisher_raises_exception(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_stub = Mock(spec=TransferResubmittingPublisher)
        transfer_resubmitting_publisher_stub.resubmit_message.side_effect = MqException()
        mailing_service_mock = Mock(spec=IMailingService)

        sut = DlqService(
            resubmitting_publisher=transfer_resubmitting_publisher_stub,
            mailing_service=mailing_service_mock,
            logger=Mock(spec=Logger)
        )

        with self.assertRaises(DlqMessageResubmittingException):
            sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_stub.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )
        self.assertIsInstance(mailing_service_mock.send_email.call_args.args[0], DlqEmailResubmitError)

    def test_handle_dlq_message_max_retries_unreached_publisher_and_mailing_service_raise_exception(
            self,
            os_getenv_mock
    ) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_stub = Mock(spec=TransferResubmittingPublisher)
        transfer_resubmitting_publisher_stub.resubmit_message.side_effect = MqException()
        mailing_service_stub = Mock(spec=IMailingService)
        mailing_service_stub.send_email.side_effect = MailingException()

        sut = DlqService(
            resubmitting_publisher=transfer_resubmitting_publisher_stub,
            mailing_service=mailing_service_stub,
            logger=Mock(spec=Logger)
        )

        with self.assertRaises(DlqEmailNotificationException):
            sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_stub.resubmit_message.assert_called_once_with(
            original_message_body=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED,
            current_retry_count=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["retry_count"],
            queue_name=self.TEST_MESSAGE_BODY_MAX_RETRIES_UNREACHED["admin_metadata"]["original_queue"]
        )
        self.assertIsInstance(mailing_service_stub.send_email.call_args.args[0], DlqEmailResubmitError)

    def test_handle_dlq_message_missing_message_fields(self, os_getenv_mock) -> None:
        os_getenv_mock.return_value = self.TEST_MESSAGE_MAX_RETRIES
        transfer_resubmitting_publisher_mock = Mock(spec=TransferResubmittingPublisher)
        mailing_service_mock = Mock(spec=IMailingService)

        sut = DlqService(
            resubmitting_publisher=transfer_resubmitting_publisher_mock,
            mailing_service=mailing_service_mock,
            logger=Mock(spec=Logger)
        )

        with self.assertRaises(DlqMessageMissingFieldException):
            sut.handle_dlq_message(self.TEST_MESSAGE_BODY_MISSING_ADMIN_METADATA, self.TEST_MESSAGE_ID)

        transfer_resubmitting_publisher_mock.resubmit_message.assert_not_called()
        self.assertIsInstance(mailing_service_mock.send_email.call_args.args[0], DlqEmailMissingMessageRequiredFields)
