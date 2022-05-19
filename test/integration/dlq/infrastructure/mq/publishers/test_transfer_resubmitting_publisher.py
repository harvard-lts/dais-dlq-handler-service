import os

from app.dlq.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher
from test.integration.dlq.infrastructure.mq.publishers.resubmitting_publisher_integration_test_base import \
    ResubmittingPublisherIntegrationTestBase


class TestTransferResubmittingPublisher(ResubmittingPublisherIntegrationTestBase):

    def test_publish_message_happy_path(self) -> None:
        sut = TransferResubmittingPublisher()
        sut.publish_message(self.TEST_ORIGINAL_MESSAGE_BODY, self.TEST_CURRENT_RETRY_COUNT, self.TEST_ORIGINAL_QUEUE)

        self._await_until_message_received_or_timeout()

        self._assert_test_message_has_been_received()

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_TRANSFER_HOST'),
            mq_port=os.getenv('MQ_TRANSFER_PORT'),
            mq_ssl_enabled=os.getenv('MQ_TRANSFER_SSL_ENABLED'),
            mq_user=os.getenv('MQ_TRANSFER_USER'),
            mq_password=os.getenv('MQ_TRANSFER_PASSWORD')
        )

    def _get_queue_name(self) -> str:
        return self.TEST_ORIGINAL_QUEUE
