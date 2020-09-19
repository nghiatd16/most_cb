from home.job import JobDescription
import logging
import json
import settings
import celery
from kombu.common import Broadcast, Queue
# from rec_core.worker import RecommendationWorker
# Celery Task wrapper
app = celery.Celery('contentbased', backend='rpc://', broker='pyamqp://{}:{}@{}:{}//'.format(settings.RABBITMQ_USER, 
                                                                                          settings.RABBITMQ_PWD, 
                                                                                          settings.RABBITMQ_HOST, 
                                                                                          settings.RABBITMQ_PORT))
app.config_from_object('celeryconfig')
app.conf.task_queues = (Broadcast('broadcast_tasks'), Queue("recommend_tasks"))
app.conf.task_routes = {
    'entrypoint.append_news': {
        # 'queue': 'broadcast_tasks',
        'exchange': 'broadcast_tasks'
    },
    'entrypoint.contentbased': {
        'queue': 'recommend_tasks'
    },
}
logging.basicConfig(level=logging.DEBUG)

def on_raw_message(body):
    print(body)
import json
import tqdm
with open("database.json") as fin:
    database = json.load(fin)
for key in tqdm.tqdm(list(database.keys())):
    url = database[key]['url']
    title = database[key]['title']
    job = JobDescription(task="push", url=url, title=title)
    # print(job.mode)
    r = app.send_task("entrypoint.contentbased", [job,])
    rs = r.get() #, propagate=False
# print(rs.to_dict())
# r = app.send_task("entrypoint.append_news", [job,], exchange='broadcast_tasks', routing_key='*')
# rs = r.get() #, propagate=False
# print(rs)
# print(JobDescription.from(rs).to_dict())
