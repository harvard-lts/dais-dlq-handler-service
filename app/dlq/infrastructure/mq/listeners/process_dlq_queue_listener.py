import os

from app.common.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.containers import Listeners
from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.infrastructure.mq.listeners.dlq_queue_listener_base import DlqQueueListenerBase


class ProcessDlqQueueListener(DlqQueueListenerBase):

    def __init__(self, dlq_service: DlqService = Listeners.process_dlq_service()) -> None:
        super().__init__(dlq_service)

    def _get_queue_name(self) -> str:
        return os.getenv('MQ_PROCESS_QUEUE_DLQ')

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_PROCESS_HOST'),
            mq_port=os.getenv('MQ_PROCESS_PORT'),
            mq_ssl_enabled=os.getenv('MQ_PROCESS_SSL_ENABLED'),
            mq_user=os.getenv('MQ_PROCESS_USER'),
            mq_password=os.getenv('MQ_PROCESS_PASSWORD')
        )
