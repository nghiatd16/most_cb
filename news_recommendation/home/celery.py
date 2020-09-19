from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_recommendation.settings')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

from kombu.common import Broadcast, Queue
# from rec_core.worker import RecommendationWorker
# Celery Task wrapper
app = Celery('most-cb', backend='rpc://', broker='pyamqp://{}:{}@{}:{}//'.format(settings.MESSAGE_BROKER['USER'], 
                                                                                settings.MESSAGE_BROKER['PASSWORD'], 
                                                                                settings.MESSAGE_BROKER['HOST'], 
                                                                                settings.MESSAGE_BROKER['PORT']))
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_queues = (Broadcast('most_broadcast_tasks'), Queue("most_recommend_tasks"))
app.conf.task_routes = {
    'most.append_news': {
        # 'queue': 'broadcast_tasks',
        'exchange': 'most_broadcast_tasks'
    },
    'most.contentbased': {
        'queue': 'most_recommend_tasks'
    },
}