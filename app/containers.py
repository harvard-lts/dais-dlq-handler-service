from dependency_injector import containers, providers

from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class Listeners(containers.DeclarativeContainer):
    transfer_resubmitting_publisher = providers.Factory(
        TransferResubmittingPublisher
    )
