import os
from typing import Tuple

from healthcheck import HealthCheck

from app.common.domain.mq.exceptions.mq_connection_exception import MqConnectionException
from app.common.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.common.infrastructure.mq.stomp_interactor import StompInteractor
from app.health.infrastructure.connectivity_service import ConnectivityService


class MqProcessConnectivityService(ConnectivityService, StompInteractor):
    __MQ_PROCESS_CONN_OK_MESSAGE = "MQ Process connection OK"
    __MQ_PROCESS_CONN_KO_MESSAGE = "MQ Process connection KO"

    def create_connectivity_check(self, health_check: HealthCheck) -> None:
        health_check.add_check(self.check_mq_process_connection)

    def check_mq_process_connection(self) -> Tuple[bool, str]:
        self._logger.info("Checking MQ Process connectivity...")
        try:
            mq_connection = self._create_mq_connection()
            mq_connection.disconnect()
            self._logger.info(self.__MQ_PROCESS_CONN_OK_MESSAGE)
            return True, self.__MQ_PROCESS_CONN_OK_MESSAGE
        except MqConnectionException:
            self._logger.info(self.__MQ_PROCESS_CONN_KO_MESSAGE)
            return False, self.__MQ_PROCESS_CONN_KO_MESSAGE

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_PROCESS_HOST'),
            mq_port=os.getenv('MQ_PROCESS_PORT'),
            mq_ssl_enabled=os.getenv('MQ_PROCESS_SSL_ENABLED'),
            mq_user=os.getenv('MQ_PROCESS_USER'),
            mq_password=os.getenv('MQ_PROCESS_PASSWORD')
        )
