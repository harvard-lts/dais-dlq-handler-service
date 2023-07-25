from celery import Celery
import os
import traceback
import logging
from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.domain.services.exceptions.dlq_service_exception import DlqServiceException

app = Celery()
app.config_from_object('celeryconfig')

retries = os.getenv('MESSAGE_MAX_RETRIES', 3)

@app.task(bind=True, serializer='json', name='ddhs.tasks.handle_dlq_message', max_retries=retries)
def handle_dlq_message(self, message_body):
    try:
        logging.getLogger('ddhs').info("Resending DLQ Message {}. Trail #{}".format(message_body, self.request.retries))
        dlq_service = DlqService()
        message_body['admin_metadata']['retry_count'] = self.request.retries
        dlq_service.handle_dlq_message(message_body, self.request.id)
        if 'testing' in message_body:
            app.send_task("dims.tasks.do_task", args=[message_body], kwargs={},
                    queue=('dlq-dryrun')) 
    except DlqServiceException as e:
        exception_msg = traceback.format_exc()
        logging.getLogger('ddhs').error(exception_msg)
        