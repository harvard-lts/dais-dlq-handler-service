from app.dlq.domain.services.exceptions.dlq_service_exception import DlqServiceException


class DlqMessageMissingFieldException(DlqServiceException):
    def __init__(self, message_id: str, field_name: str) -> None:
        self.message = f"DLQ message with id {message_id} does not contain {field_name} field inside body"
        super().__init__(self.message)
