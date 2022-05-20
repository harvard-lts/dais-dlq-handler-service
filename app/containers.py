from dependency_injector import containers, providers

from app.dlq.infrastructure.mq.publishers.process_resubmitting_publisher import ProcessResubmittingPublisher
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class Listeners(containers.DeclarativeContainer):
    process_resubmitting_publisher = providers.Factory(
        ProcessResubmittingPublisher
    )
    transfer_resubmitting_publisher = providers.Factory(
        TransferResubmittingPublisher
    )
