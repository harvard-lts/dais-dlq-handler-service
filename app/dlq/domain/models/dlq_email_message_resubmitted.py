from app.dlq.domain.models.dlq_email import DlqEmail


class DlqEmailMessageResubmitted(DlqEmail):
    __BODY_TEMPLATE = "Message with id {} has been resubmitted to its original queue."

    subject = "Message resubmitted"

    def __init__(self, message_id: str) -> None:
        super().__init__()
        self.body = self.__BODY_TEMPLATE.format(message_id)
