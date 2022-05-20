from app.common.domain.mq.exceptions.mq_exception import MqException


class MqMessagePublishException(MqException):
    def __init__(self, queue_name: str, queue_host: str, queue_port: str, reason: str) -> None:
        message = f"An error occurred while publishing message to queue {queue_name} on host " \
                  f"{queue_host}, port {queue_port}"
        if reason:
            message = message + f". Reason was: {reason}"
        super().__init__(message)
