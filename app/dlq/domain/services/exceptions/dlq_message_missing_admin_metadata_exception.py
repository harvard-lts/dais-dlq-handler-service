from app.dlq.domain.services.exceptions.dlq_service_exception import DlqServiceException


class DlqMessageMissingAdminMetadataException(DlqServiceException):
    def __init__(self, message_id: str) -> None:
        self.message = f"DLQ message with id {message_id} does not contain admin_metadata field inside body"
        super().__init__(self.message)
