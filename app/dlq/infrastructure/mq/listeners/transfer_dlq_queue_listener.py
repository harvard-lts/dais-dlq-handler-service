import os

from app.common.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.containers import Listeners
from app.dlq.infrastructure.mq.listeners.dlq_queue_listener_base import DlqQueueListenerBase
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class TransferDlqQueueListener(DlqQueueListenerBase):

    def __init__(
            self,
            transfer_resubmitting_publisher: TransferResubmittingPublisher = Listeners.transfer_resubmitting_publisher()
    ) -> None:
        super().__init__(transfer_resubmitting_publisher)

    def _get_queue_name(self) -> str:
        return os.getenv('MQ_TRANSFER_QUEUE_DLQ')

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_TRANSFER_HOST'),
            mq_port=os.getenv('MQ_TRANSFER_PORT'),
            mq_ssl_enabled=os.getenv('MQ_TRANSFER_SSL_ENABLED'),
            mq_user=os.getenv('MQ_TRANSFER_USER'),
            mq_password=os.getenv('MQ_TRANSFER_PASSWORD')
        )
