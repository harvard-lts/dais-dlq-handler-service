from app.dlq.domain.models.dlq_email import DlqEmail
from app.dlq.domain.models.dlq_email_message_max_retries_reached import DlqEmailMaxRetriesReached
from app.dlq.domain.models.dlq_email_message_resubmitted import DlqEmailMessageResubmitted
from app.dlq.domain.models.dlq_email_missing_message_required_fields import DlqEmailMissingMessageRequiredFields
from app.dlq.domain.models.dlq_email_reason import DlqEmailReason
from app.dlq.domain.models.dlq_email_resubmit_error import DlqEmailResubmitError


class DlqEmailFactory:

    def get_dlq_email(self, reason: DlqEmailReason, message_id: str) -> DlqEmail:
        return {
            reason.MISSING_MESSAGE_REQUIRED_FIELDS: DlqEmailMissingMessageRequiredFields(message_id),
            reason.MAX_RETRIES_REACHED: DlqEmailMaxRetriesReached(message_id),
            reason.MESSAGE_RESUBMITTED: DlqEmailMessageResubmitted(message_id),
            reason.RESUBMIT_ERROR: DlqEmailResubmitError(message_id),
        }.get(reason, "")
