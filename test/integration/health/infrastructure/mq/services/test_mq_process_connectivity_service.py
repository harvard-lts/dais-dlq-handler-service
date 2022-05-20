from app.health.infrastructure.mq.services.mq_process_connectivity_service import MqProcessConnectivityService
from test.integration.integration_test_base import IntegrationTestBase


class TestMqProcessConnectivityService(IntegrationTestBase):

    def test_check_mq_process_connection_happy_path(self) -> None:
        sut = MqProcessConnectivityService()

        actual_result_status, actual_result_message = sut.check_mq_process_connection()

        self.assertTrue(actual_result_status)
        expected_result_message = "MQ Process connection OK"
        self.assertEqual(actual_result_message, expected_result_message)
