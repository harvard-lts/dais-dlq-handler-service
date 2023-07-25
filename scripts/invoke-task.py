from celery import Celery
import os

app1 = Celery('tasks')
app1.config_from_object('celeryconfig')
        
arguments = {
            'testing': "true",
            "admin_metadata": {"original_queue": "test-dlq", 
                               "task_name": "nameof.task",
                               "retry_count": 0}}

res = app1.send_task('ddhs.tasks.handle_dlq_message',
                     args=[arguments], kwargs={},
                     queue=os.getenv("CONSUME_QUEUE_NAME"),
                     expiration=os.getenv('MESSAGE_EXPIRATION_MS', 10000))
