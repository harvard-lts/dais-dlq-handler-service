import os

from app.dlq.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.dlq.infrastructure.mq.publishers.resubmitting_publisher_base import ResubmittingPublisherBase


class TransferResubmittingPublisher(ResubmittingPublisherBase):

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_TRANSFER_HOST'),
            mq_port=os.getenv('MQ_TRANSFER_PORT'),
            mq_ssl_enabled=os.getenv('MQ_TRANSFER_SSL_ENABLED'),
            mq_user=os.getenv('MQ_TRANSFER_USER'),
            mq_password=os.getenv('MQ_TRANSFER_PASSWORD')
        )
