from . import preprocess
from . import constants as c
import numpy as np
import settings
import os
import logging
import tensorflow as tf
import keras
# Turn off bytecode generation
import sys
sys.dont_write_bytecode = True

# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django
django.setup()
import sys
sys.path.append("..")
from home.models import News, User, History

class RecommendationWorker:
    def __init__(self):
        print("Loading Deep Model")
        self.device="cpu"
        user_presentation_model_path = os.path.join(settings.BASE_DIR, "resource", "user_presentation_v2.h5")
        encoder_model_path = os.path.join(settings.BASE_DIR, "resource", "encoder_v2.h5")
        self.user_presentation_model = keras.models.load_model(user_presentation_model_path)
        self.encoder_model = keras.models.load_model(encoder_model_path)
        logging.info("Load model success")

        # Loading database
        print("Loading news embedding from database")
        all_news = News.objects.exclude(embedding=None)
        list_labels = list()
        list_embeddings = list()
        self.dbid_to_lbid = dict() # Find position of items in self.list_embeddings by news_id
        self.lbid_to_dbid = dict() # Find news_id by position in self.list_embeddings
        for lbid, news in enumerate(all_news):
            list_labels.append(news.id)
            list_embeddings.append(np.frombuffer(news.embedding, dtype=np.float32))
            self.dbid_to_lbid[news.id] = lbid
            self.lbid_to_dbid[lbid] = news.id
        self.list_labels = list_labels
        if len(list_embeddings) > 0:
            self.list_embeddings = np.stack(list_embeddings)
        else:
            self.list_embeddings = np.array([])
        logging.info("self.list_embeddings.shape: " + str(self.list_embeddings.shape))
        print("Loading all component successfull")
    
    @classmethod
    def _split_batch(cls, input_tensor, batch_size):
        endpoint = input_tensor.shape[0] // batch_size + 1
        split_pos = np.arange(1*batch_size, endpoint*batch_size, step=batch_size)
        splited_array = np.split(input_tensor, split_pos)
        if splited_array[-1].shape[0] == 0:
            del splited_array[-1]
        return splited_array

    def get_browsed_embedding(self, browsed_news):
        if len(browsed_news) == 0:
            return np.array([], dtype=np.float32)
        preprocessed_browsed = preprocess.preprocess_browsed_news(browsed_news)
        browsed_title_split=[preprocessed_browsed[:,k,:] for k in range(preprocessed_browsed.shape[1])]
        result = self.user_presentation_model.predict(browsed_title_split)[0]
        result.astype(np.float32)
        return result
    
    def get_news_embedding(self, news, batch_size=64):
        if len(news) == 0:
            return np.array([], dtype=np.float32)
        preprocessed_news = preprocess.preprocess_candidate_news(news)
        batch_splited_news = self._split_batch(preprocessed_news, batch_size)
        result = []
        for batch in batch_splited_news:
            batch_splited = [batch[:,k,:] for k in range(batch.shape[1])]
            mini_rs = self.encoder_model.predict(batch_splited)[0]
            result.append(mini_rs)
        result = np.stack(result)
        result.astype(np.float32)
        return result
    
    def recommend_for_user(self, browsed_items, num_items=10):
        browsed_items = browsed_items[:c.MAX_SENTS]
        browsed_titles = [item['title'] for item in browsed_items]
        if len(browsed_items) == 0:
            return [], browsed_items
        if len(self.list_embeddings) == 0:
            return [], browsed_items
        user_embedding = self.get_browsed_embedding(browsed_titles)
        # print("user_embedding.shape", user_embedding.shape)
        # print("self.list_embeddings.shape", self.list_embeddings.shape)
        score_matrix = np.matmul(user_embedding, self.list_embeddings.T)
        # print("score_matrix", score_matrix)
        # print("score_matrix.shape", score_matrix.shape)
        ranked_similarity_score = score_matrix.argsort()[-num_items:][::-1]
        # print("ranked_similarity_score", ranked_similarity_score)
        # print("ranked_similarity_score.shape", ranked_similarity_score.shape)
        rec_items_id = [self.lbid_to_dbid[lbid] for lbid in ranked_similarity_score]
        recommended_news = News.objects.filter(id__in=rec_items_id)
        return recommended_news, browsed_items
    
    def add_new_items_to_memory(self, news_id, news_embedding):
        # logging.info("Append news")
        self.list_labels.append(news_id)
        lbid = len(self.list_labels)-1
        self.dbid_to_lbid[news_id] = lbid
        self.lbid_to_dbid[lbid] = news_id
        if news_embedding.ndim == 1:
            news_embedding = np.expand_dims(news_embedding, 0)
        logging.info(f"news_embedding_shape: {news_embedding.shape}")
        logging.info(f"list_embeddings: {self.list_embeddings.shape}")
        if len(self.list_embeddings) > 0:
            self.list_embeddings = np.append(self.list_embeddings, news_embedding, axis=0)
        else:
            self.list_embeddings = np.array(news_embedding)