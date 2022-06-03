import logging

from dependency_injector import containers, providers

from app.common.infrastructure.mailing.smtp_mailing_service import SmtpMailingService
from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.infrastructure.mq.publishers.process_resubmitting_publisher import ProcessResubmittingPublisher
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class Listeners(containers.DeclarativeContainer):
    logger = logging.getLogger()
    mailing_service = SmtpMailingService()

    process_dlq_service = providers.Factory(
        DlqService,
        resubmitting_publisher=ProcessResubmittingPublisher(),
        mailing_service=mailing_service,
        logger=logger
    )

    transfer_dlq_service = providers.Factory(
        DlqService,
        resubmitting_publisher=TransferResubmittingPublisher(),
        mailing_service=mailing_service,
        logger=logger
    )
