from django.urls import path, include
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # path('add_history/', views.add_user_history),
    path('content-based/', views.get_recommedation)
]   