from app.dlq.domain.models.dlq_email import DlqEmail
from app.dlq.domain.models.dlq_email_message_max_retries_reached import DlqEmailMaxRetriesReached
from app.dlq.domain.models.dlq_email_message_resubmitted import DlqEmailMessageResubmitted
from app.dlq.domain.models.dlq_email_reason import DlqEmailReason
from app.dlq.domain.models.dlq_email_resubmit_error import DlqEmailResubmitError


class DlqEmailFactory:

    def get_dlq_email(self, reason: DlqEmailReason, message_id: str) -> DlqEmail:
        return {
            reason.MAX_RETRIES_REACHED: DlqEmailMaxRetriesReached(message_id),
            reason.MESSAGE_RESUBMITTED: DlqEmailMessageResubmitted(message_id),
            reason.RESUBMIT_ERROR: DlqEmailResubmitError(message_id),
        }.get(reason, "")
