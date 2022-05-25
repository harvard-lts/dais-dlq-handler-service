from abc import ABC

from test.integration.dlq.infrastructure.mq.publishers.stomp_publisher_integration_test_base import \
    StompPublisherIntegrationTestBase


class ResubmittingPublisherIntegrationTestBase(StompPublisherIntegrationTestBase, ABC):

    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_ORIGINAL_QUEUE = "test_queue"
        cls.TEST_CURRENT_RETRY_COUNT = 2
        cls.TEST_ORIGINAL_MESSAGE_BODY = {
            "test": "test",
            "admin_metadata": {
                "original_queue": cls.TEST_ORIGINAL_QUEUE,
                "retry_count": cls.TEST_CURRENT_RETRY_COUNT
            }
        }

    def _get_expected_body(self) -> dict:
        expected_body = self.TEST_ORIGINAL_MESSAGE_BODY
        expected_body['admin_metadata']['retry_count'] = self.TEST_CURRENT_RETRY_COUNT + 1
        return expected_body
