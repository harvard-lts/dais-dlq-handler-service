from abc import ABC, abstractmethod

from healthcheck import HealthCheck


class ConnectivityService(ABC):

    @abstractmethod
    def create_connectivity_check(self, health_check: HealthCheck) -> None:
        pass
