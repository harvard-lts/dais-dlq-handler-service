"""
This module defines a StompListenerBase, which is an abstract class intended
to define common behavior for stomp-implemented MQ listener components.
"""
import json
from abc import abstractmethod, ABC

import stomp
from stomp.utils import Frame

from app.dlq.infrastructure.mq.stomp_interactor import StompInteractor


class StompListenerBase(stomp.ConnectionListener, StompInteractor, ABC):
    __ACK_CLIENT_INDIVIDUAL = "client-individual"

    def __init__(self) -> None:
        super().__init__()
        self.__reconnect_on_disconnection = True
        self._connection = self.__create_subscribed_mq_connection()

    def on_message(self, frame: Frame) -> None:
        try:
            message_body = json.loads(frame.body)
        except json.decoder.JSONDecodeError as e:
            self._logger.error(str(e))
            raise e

        self._handle_received_message(message_body, frame.headers['message-id'], frame.headers['subscription'])

    def on_error(self, frame: Frame) -> None:
        self._logger.info("MQ error received: " + frame.body)

    def on_disconnected(self) -> None:
        self._logger.debug("Disconnected from MQ")
        if self.__reconnect_on_disconnection:
            self._logger.debug("Reconnecting to MQ...")
            self.reconnect()

    def reconnect(self) -> None:
        self.__reconnect_on_disconnection = True
        self._connection = self.__create_subscribed_mq_connection()

    def disconnect(self) -> None:
        self.__reconnect_on_disconnection = False
        self._connection.disconnect()

    @abstractmethod
    def _get_queue_name(self) -> str:
        """
        Retrieves the name of the queue to listen to
        """

    @abstractmethod
    def _handle_received_message(self, message_body: dict, message_id: str, message_subscription: str) -> None:
        """
        Handles the received message by adding child listener specific logic.

        :param message_body: received message body
        :type message_body: dict
        :param message_id: received message id
        :type message_id: str
        :param message_subscription: received message subscription
        :type message_subscription: str
        """

    def __create_subscribed_mq_connection(self) -> stomp.Connection:
        connection = self._create_mq_connection()
        connection.subscribe(destination=self._get_queue_name(), id=1, ack=self.__ACK_CLIENT_INDIVIDUAL)
        connection.set_listener('', self)
        return connection
