from app.common.domain.mailing.email import Email
from app.common.infrastructure.mailing.smtp_mailing_service import SmtpMailingService
from unittest import TestCase


class TestSmtpMailingService(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_EMAIL = Email()
        cls.TEST_EMAIL.subject = "HDC3A DLQ Test Email"
        cls.TEST_EMAIL.body = "This is an automated test email sent from HDC3A DLQ Handler Service integration tests."

    def test_send_email_happy_path(self) -> None:
        sut = SmtpMailingService()
        sut.send_email(self.TEST_EMAIL)
