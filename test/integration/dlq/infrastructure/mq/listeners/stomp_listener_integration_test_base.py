import json
import time
from abc import ABC

from test.integration.dlq.infrastructure.mq.stomp_integration_test_base import StompIntegrationTestBase


class StompListenerIntegrationTestBase(StompIntegrationTestBase, ABC):

    def _send_test_message(self, message_body: dict) -> None:
        test_message_json_str = json.dumps(message_body)

        connection = self._create_mq_connection()
        connection.send(self._get_queue_name(), test_message_json_str)
        connection.disconnect()

    def _await_until_on_message_has_calls_or_timeout(self, on_message_mock) -> None:
        timeout = self._get_message_await_timeout()
        while not on_message_mock.call_count and time.time() < timeout:
            time.sleep(1)

    def _assert_on_message_has_calls(self, on_message_mock) -> None:
        if on_message_mock.call_count == 0:
            self.fail(msg="The listener did not receive the published message")
