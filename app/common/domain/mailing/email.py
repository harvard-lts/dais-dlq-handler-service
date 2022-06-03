from abc import ABC


class Email(ABC):
    subject: str
    body: str
