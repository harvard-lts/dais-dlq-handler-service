from app.dlq.domain.services.exceptions.dlq_service_exception import DlqServiceException


class DlqEmailNotificationException(DlqServiceException):
    def __init__(self, message_id: str, reason: str) -> None:
        self.message = f"Error while sending notification email for message with id {message_id}. Reason was: {reason}"
        super().__init__(self.message)
