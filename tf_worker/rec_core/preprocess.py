import json
import numpy as np
from vncorenlp import VnCoreNLP
import itertools
from . import constants as c
import settings
import os


vncorenlp_path = os.path.join(settings.BASE_DIR, "resource", "VnCoreNLP-1.1.1.jar") 
# print(vncorenlp_path)
annotator = VnCoreNLP(vncorenlp_path, annotators="wseg", max_heap_size='-Xmx2g') 
# annotator = VnCoreNLP(address="http://0.0.0.0", port=9090)
print("Connected to VnCoreNLP")
word_dict_path = os.path.join(settings.BASE_DIR, "resource", "word_dict.json")
with open(word_dict_path, "r") as fin:
    word_dict = json.load(fin)

def process_sentence(sentence, max_length, language="vietnamese"):
    sentence = sentence[:2000]
    sentence = sentence.replace("\\t", " ")
    sentence = sentence.replace("\\n", " ")
    sentence = sentence.replace("\xa0", " ")
    sentence = sentence.replace(")", " ")
    sentence = sentence.replace("(", " ")
    sentence = sentence.replace("{", " ")
    sentence = sentence.replace("}", " ")
    sentence = sentence.replace("[", " ")
    sentence = sentence.replace("]", " ")
    sentence = sentence.replace("'", " ")
    sentence = sentence.replace(";", " ")
    sentence = sentence.replace(":", " ")
    sentence = sentence.replace(",", " ")
    sentence = sentence.replace(".", " ")
    sentence = sentence.replace("-", " ")
    if language == "vietnamese":
        sentences = annotator.tokenize(sentence.lower())
        return list(itertools.chain(*sentences))[:max_length]
    else:
        import nltk
        return nltk.word_tokenize(sentence, language=language)[:max_length]
    return None

def preprocess_browsed_news(list_titles):
    list_browsed = list()

    # Load preprocessed titles and bodies from json
    for title in list_titles:
        processed_title = process_sentence(title, c.MAX_SENT_LENGTH)
        
        list_browsed.append(processed_title)

    browsed_news = []

    for news in list_browsed:
        word_id=[]
        list_preprocessed_titles = news
        for word in list_preprocessed_titles:
            if word in word_dict:
                word_id.append(word_dict[word][0])
        word_id=word_id[:c.MAX_SENT_LENGTH]
        browsed_news.append(word_id+[0]*(c.MAX_SENT_LENGTH-len(word_id)))
    if len(browsed_news) < c.MAX_SENTS:
        padding = [[0] * c.MAX_SENT_LENGTH] * (c.MAX_SENTS - len(browsed_news))
        browsed_news.extend(padding)
    else:
        browsed_news = browsed_news[-c.MAX_SENTS:]
    browsed_news=np.array([browsed_news],dtype='int32')

    return browsed_news

def preprocess_candidate_news(list_candidate_titles):
    list_candidate = list()

    # Load preprocessed titles and bodies from json
    for candidate_title in list_candidate_titles:
        processed_candidate_title = process_sentence(candidate_title, c.MAX_SENT_LENGTH)
        
        list_candidate.append(processed_candidate_title)

    candidate_news = []

    for news in list_candidate:
        word_id=[]
        list_preprocessed_titles = news
        for word in list_preprocessed_titles:
            if word in word_dict:
                word_id.append(word_dict[word][0])
        word_id=word_id[:c.MAX_SENT_LENGTH]
        candidate_news.append(word_id+[0]*(c.MAX_SENT_LENGTH-len(word_id)))

    candidate_news=np.array([candidate_news],dtype='int32')

    return candidate_news