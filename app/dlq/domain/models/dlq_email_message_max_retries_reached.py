from app.dlq.domain.models.dlq_email import DlqEmail


class DlqEmailMaxRetriesReached(DlqEmail):
    __BODY_TEMPLATE = "Maximum resubmitting retries reached for message with id {}.\n\n" \
                      "The message has been consumed and will not be resubmitted again."

    subject = "Message maximum resubmitting retries reached"

    def __init__(self, message_id: str) -> None:
        super().__init__()
        self.body = self.__BODY_TEMPLATE.format(message_id)
