import os
from abc import ABC

from app.common.domain.mailing.email import Email


class DlqEmail(Email, ABC):
    __SUBJECT_TEMPLATE = "HDC3A DLQ {}: {}"

    def __init__(self) -> None:
        self.subject = self.__SUBJECT_TEMPLATE.format(self.__get_environment(), self.subject)

    def __get_environment(self) -> str:
        return os.getenv('HDHS_ENVIRONMENT')
