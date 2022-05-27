from app.health.infrastructure.mq.services.mq_transfer_connectivity_service import MqTransferConnectivityService
from test.integration.integration_test_base import IntegrationTestBase


class TestMqTransferConnectivityService(IntegrationTestBase):

    def test_check_mq_transfer_connection_happy_path(self) -> None:
        sut = MqTransferConnectivityService()

        actual_result_status, actual_result_message = sut.check_mq_transfer_connection()

        self.assertTrue(actual_result_status)
        expected_result_message = "MQ Transfer connection OK"
        self.assertEqual(actual_result_message, expected_result_message)
