from .models import User, News, History
from rest_framework import serializers
from django.conf import settings
import os
import glob
import shutil
import logging
import time

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username']

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['url', 'id', 'title', 'embedding']
    
    def create(self, validated_data):
        title = validated_data['title']
        # embedding = GLOBAL_WORKER.get_news_embedding([title])[0]
        # # Convert embedding to bytes
        # embedding_bytes = embedding.tobytes()
        n_news = News(title=title, embedding=None)
        n_news.save()
        return n_news
    
    def update(self, instance, validated_data):
        title = validated_data['title']
        # embedding = GLOBAL_WORKER.get_news_embedding([title])[0]
        # # Convert embedding to bytes
        # embedding_bytes = embedding.tobytes()
        # instance.embedding = embedding_bytes
        instance.save()
        return instance
