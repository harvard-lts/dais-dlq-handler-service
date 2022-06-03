from app.dlq.domain.models.dlq_email import DlqEmail


class DlqEmailMissingMessageRequiredFields(DlqEmail):
    __BODY_TEMPLATE = "The message with id {} has missing required fields.\n\n" \
                      "The message will remain as pending in the DLQ."

    subject = "Missing message required fields"

    def __init__(self, message_id: str) -> None:
        super().__init__()
        self.body = self.__BODY_TEMPLATE.format(message_id)
