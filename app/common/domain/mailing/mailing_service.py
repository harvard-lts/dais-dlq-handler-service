"""
This module defines an IMailingService, which is a domain interface
that defines the necessary methods to implement by a mailing service.
"""

from abc import ABC, abstractmethod

from app.common.domain.mailing.email import Email


class IMailingService(ABC):

    @abstractmethod
    def send_email(self, email: Email) -> None:
        """
        Sends an email.

        :param email: Email to send
        :type email: Email

        :raises MailingException
        """
