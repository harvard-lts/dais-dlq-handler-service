from enum import Enum


class DlqEmailReason(Enum):
    RESUBMIT_ERROR = 1
    MAX_RETRIES_REACHED = 2
    MESSAGE_RESUBMITTED = 3
