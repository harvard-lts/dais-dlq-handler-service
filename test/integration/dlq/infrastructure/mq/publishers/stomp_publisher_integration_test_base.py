import json
import time
from abc import ABC, abstractmethod

import stomp
from stomp.utils import Frame

from test.integration.dlq.infrastructure.mq.stomp_integration_test_base import StompIntegrationTestBase


class StompPublisherIntegrationTestBase(StompIntegrationTestBase, ABC):

    def setUp(self) -> None:
        super().setUp()
        self.received_frame = None
        self.connection = self._create_subscribed_mq_connection()

    def tearDown(self) -> None:
        self.connection.disconnect()

    def _create_subscribed_mq_connection(self) -> stomp.Connection:
        connection = self._create_mq_connection()

        subscription_id = self._get_queue_name() + "-test-connection"
        connection.subscribe(destination=self._get_queue_name(), id=subscription_id)

        listener_name = self._get_queue_name() + "-test-listener"
        connection.set_listener(listener_name, StompPublisherIntegrationTestBase.TestConnectionListener(self))

        return connection

    def _await_until_message_received_or_timeout(self) -> None:
        timeout = self._get_message_await_timeout()
        while self.received_frame is None and time.time() < timeout:
            time.sleep(1)

    def _assert_test_message_has_been_received(self) -> None:
        if self.received_frame is None:
            self.fail(msg="The queue did not receive the published message")

        actual_body = json.loads(self.received_frame.body)
        expected_body = self._get_expected_body()
        self.assertDictEqual(actual_body, expected_body)

        actual_expires_header = self.received_frame.headers.get('expires', None)
        self.assertIsNotNone(actual_expires_header)

        actual_persistent_header = self.received_frame.headers['persistent']
        expected_persistent_header = "true"
        self.assertEqual(actual_persistent_header, expected_persistent_header)

    @abstractmethod
    def _get_expected_body(self) -> dict:
        pass

    class TestConnectionListener(stomp.ConnectionListener):
        def __init__(self, outer_test) -> None:
            self.outer_test = outer_test

        def on_message(self, frame: Frame) -> None:
            self.outer_test.received_frame = frame
