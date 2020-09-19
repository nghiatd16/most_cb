from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
# Create your models here.

class News(models.Model):
    url = models.TextField()
    title = models.TextField()
    upload_time = models.DateTimeField(auto_now_add=True)
    embedding = models.BinaryField(null=True)

    def __str__(self):
        return f"{self.title} - {self.upload_time}"

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clicked_news = models.ForeignKey(News, on_delete=models.CASCADE)
    clicked_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.clicked_news.title}"