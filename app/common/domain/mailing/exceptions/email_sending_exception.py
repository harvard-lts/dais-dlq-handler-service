from app.common.domain.mailing.exceptions.mailing_exception import MailingException


class EmailSendingException(MailingException):
    def __init__(self, email_host: str, email_port: str, email_message: str, reason: str) -> None:
        message = f"An error occurred while sending email to host {email_host}, port {email_port}, " \
                  f"with message {email_message}"
        if reason:
            message = message + f". Reason was: {reason}"
        super().__init__(message)
