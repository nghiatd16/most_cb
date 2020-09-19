import settings
from home.job import JobDescription
from rec_core.worker import RecommendationWorker
from home.models import News
import celery
import logging
logging.basicConfig(level=logging.DEBUG)
from kombu.common import Broadcast, Queue


# Celery Task wrapper
app = celery.Celery('most-cb', backend='rpc://', broker='pyamqp://{}:{}@{}:{}//'.format(settings.RABBITMQ_USER, 
                                                                                          settings.RABBITMQ_PWD, 
                                                                                          settings.RABBITMQ_HOST, 
                                                                                          settings.RABBITMQ_PORT))
app.config_from_object('celeryconfig')
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
worker =  RecommendationWorker()


@app.task
def contentbased(job_description):
    if job_description.task == "get_browsed_embedding":
        browsed_news = job_description.data
        browsed_embedding = worker.get_browsed_embedding(browsed_news)
        return JobDescription(task=job_description.task, device=worker.device, result=browsed_embedding)
    elif job_description.task == "get_news_embedding":
        news = job_description.data
        news_embedding = worker.get_news_embedding(news)
        return JobDescription(task=job_description.task, device=worker.device, result=news_embedding)
    else:
        browsed_items = job_description.browsed_items
        recommended_items, browsed_items = worker.recommend_for_user(browsed_items)
        return JobDescription(task=job_description.task, device=worker.device, result={"recommended_items": recommended_items, "browsed_items": browsed_items})
@app.task
def append_news(job_description):
    news_id = job_description.news_id
    news_embedding = job_description.news_embedding
    worker.add_new_items_to_memory(news_id, news_embedding)
    return JobDescription(msg = "ok")

# if __name__ == "__main__":
#     import tqdm
#     all_news = News.objects.all()
#     total = len(all_news)
#     with tqdm.tqdm(total=total) as pbar:
#         for news in all_news:
#             title = news.title
#             news_embedding = worker.get_news_embedding([title])
#             embedding = news_embedding[0]
#             embedding_bytes = embedding.tobytes()
#             news.embedding = embedding_bytes
#             news.save()
#             pbar.update()
        