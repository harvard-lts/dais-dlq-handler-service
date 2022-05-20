import time
from abc import abstractmethod, ABC

import stomp

from app.common.infrastructure.mq.mq_connection_params import MqConnectionParams
from test.integration.integration_test_base import IntegrationTestBase


class StompIntegrationTestBase(IntegrationTestBase, ABC):
    __STOMP_CONN_HEARTBEATS_MS = 40000
    __MESSAGE_AWAIT_TIMEOUT_SECONDS = 30

    def _create_mq_connection(self) -> stomp.Connection:
        mq_connection_params = self._get_mq_connection_params()

        mq_host = mq_connection_params.mq_host
        mq_port = mq_connection_params.mq_port
        mq_ssl_enabled = mq_connection_params.mq_ssl_enabled
        mq_user = mq_connection_params.mq_user
        mq_password = mq_connection_params.mq_password

        connection = stomp.Connection(
            host_and_ports=[(mq_host, mq_port)],
            heartbeats=(self.__STOMP_CONN_HEARTBEATS_MS, self.__STOMP_CONN_HEARTBEATS_MS),
            keepalive=True
        )

        if mq_ssl_enabled == 'True':
            connection.set_ssl([(mq_host, mq_port)])

        connection.connect(
            mq_user,
            mq_password,
            wait=True
        )

        return connection

    @abstractmethod
    def _get_mq_connection_params(self) -> MqConnectionParams:
        pass

    @abstractmethod
    def _get_queue_name(self) -> str:
        pass

    def _get_message_await_timeout(self) -> float:
        return time.time() + self.__MESSAGE_AWAIT_TIMEOUT_SECONDS
