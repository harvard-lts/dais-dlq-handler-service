from app.dlq.domain.models.dlq_email import DlqEmail


class DlqEmailResubmitError(DlqEmail):
    __BODY_TEMPLATE = "There was an error when resubmitting message with id {} to its original queue.\n\n" \
                      "The message will remain as pending in the DLQ."

    subject = "Message publishing error"

    def __init__(self, message_id: str) -> None:
        super().__init__()
        self.body = self.__BODY_TEMPLATE.format(message_id)
