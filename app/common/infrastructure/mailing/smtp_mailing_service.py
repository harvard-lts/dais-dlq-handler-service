import logging
import os
import smtplib
from email.message import EmailMessage

from tenacity import retry, stop_after_attempt, retry_if_exception_type, before_log

from app.common.domain.mailing.email import Email
from app.common.domain.mailing.exceptions.email_sending_exception import EmailSendingException
from app.common.domain.mailing.mailing_service import IMailingService


class SmtpMailingService(IMailingService):
    __SMTP_SEND_MESSAGE_MAX_RETRIES = 2

    def __init__(self) -> None:
        self.__logger = logging.getLogger()

    def send_email(self, email: Email) -> None:
        message = self.__create_message(email.subject, email.body)
        self.__send_smtp_message(message)

    def __create_message(self, email_subject: str, email_body: str) -> EmailMessage:
        self.__logger.info("Creating email message with subject {} and body {}...".format(email_subject, email_body))

        email_sender = os.getenv("EMAIL_SENDER")
        email_destinatary = os.getenv("EMAIL_DESTINATARY")
        self.__logger.info(
            "Sender is {}, and destinatary is {}, for email with subject {}".format(
                email_sender,
                email_destinatary,
                email_subject
            )
        )

        message = EmailMessage()
        message.set_content(email_body)

        message['Subject'] = email_subject
        message['From'] = email_sender
        message['To'] = email_destinatary

        return message

    @retry(
        stop=stop_after_attempt(__SMTP_SEND_MESSAGE_MAX_RETRIES),
        retry=retry_if_exception_type(EmailSendingException),
        reraise=True,
        before=before_log(logging.getLogger(), logging.INFO)
    )
    def __send_smtp_message(self, message: EmailMessage) -> None:
        email_host = os.getenv("EMAIL_HOST")
        email_port = os.getenv("EMAIL_PORT")
        self.__logger.info(
            "Sending email with subject {} to host {}, port {}, via SMTP...".format(
                message['Subject'],
                email_host,
                email_port
            )
        )
        try:
            smtp = smtplib.SMTP(email_host, email_port)
            smtp.send_message(message)
            smtp.quit()
            self.__logger.info("Email sent")
        except smtplib.SMTPException as e:
            self.__logger.error(str(e))
            raise EmailSendingException(email_host, email_port, message.as_string(), str(e))
