from app.dlq.domain.services.exceptions.dlq_service_exception import DlqServiceException


class DlqMessageResubmittingException(DlqServiceException):
    def __init__(self, message_id: str, reason: str) -> None:
        self.message = f"There was an error when resubmitting DLQ message with id {message_id}. Reason was: {reason}"
        super().__init__(self.message)
