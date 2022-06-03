from enum import Enum


class DlqEmailReason(Enum):
    MISSING_MESSAGE_REQUIRED_FIELDS = 1
    RESUBMIT_ERROR = 2
    MAX_RETRIES_REACHED = 3
    MESSAGE_RESUBMITTED = 4
