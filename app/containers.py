import logging

from dependency_injector import containers, providers

from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.infrastructure.mq.publishers.process_resubmitting_publisher import ProcessResubmittingPublisher
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class Listeners(containers.DeclarativeContainer):
    logger = logging.getLogger()

    process_dlq_service = providers.Factory(
        DlqService,
        resubmitting_publisher=ProcessResubmittingPublisher,
        logger=logging.getLogger()
    )

    transfer_dlq_service = providers.Factory(
        DlqService,
        resubmitting_publisher=TransferResubmittingPublisher,
        logger=logger
    )
