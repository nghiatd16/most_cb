from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, JsonResponse
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
import json
import time
from .job import JobDescription
# from .forms import *
from django.views import View
from rest_framework.decorators import api_view
from .celery import app
import traceback

class UserViewSet(viewsets.ModelViewSet):
    """
    API cho phép xem, thêm, sửa, xóa các user
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend,]
    filter_fields = ['username', ]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class NewsViewSet(viewsets.ModelViewSet):
    """
    API cho phép xem, thêm, sửa, xóa các news.
    """
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset.values_list("id", "title"))
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

@api_view(["GET", "POST"])
@permission_classes((permissions.AllowAny,))
def get_recommedation(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
        except:
            return JsonResponse({'status':'false','message': 'Request body must be a json string'}, status=400)
        try:
            user_id = request_data['deviceid']
            browsed_items = request_data['browsed_items']
        except Exception as e:
            return JsonResponse({'status':'false','message': e.__str__()}, status=400)
        if User.objects.filter(username=user_id).exists():
            user = User.objects.get(username=user_id)
        else:
            user = User(username=user_id)
            user.set_password("password")
            user.save()
        # Extract browsed_items
        try:
            for item in browsed_items:
                url = item['url'].strip()
                title = item['title'].strip()
                if not News.objects.filter(url=url).exists():
                    # Get news embedding
                    job = JobDescription(task="get_news_embedding", data=[title])
                    r = app.send_task("most.contentbased", [job,])
                    response = r.get()
                    embedding = response.result[0]
                    # Save to database
                    ## Convert embedding to bytes
                    embedding_bytes = embedding.tobytes()
                    news = News(url=url, title=title, embedding=embedding_bytes)
                    news.save()
                    # Broadcast to all workers to update memory
                    job = JobDescription(news_id=news.id, news_embedding=embedding)
                    app.send_task("most.append_news", [job,], exchange='broadcast_tasks', routing_key='*')
        except:
            
            traceback.print_exc()
            return JsonResponse({"status": "false", "message": "Browsed_items has wrong format"}, status=400)
        
        #Get recommended items
        job = JobDescription(task="get_recommendation", browsed_items=browsed_items)
        r = app.send_task("most.contentbased", [job,])
        response = r.get()
        result, browsed_items = response.result['recommended_items'], response.result['browsed_items']
        resp_recommended_items = list()
        last_clicked_item_title = browsed_items[-1]['title'].strip().lower()
        for resp_news in result:
            title = resp_news.title.strip()
            if title.lower() != last_clicked_item_title:
                resp_recommended_items.append({
                    "url": resp_news.url,
                    "title": resp_news.title
                })
        
        rs_dict = {
            "status": "true",
            "user": user.username,
            "recommended_items": resp_recommended_items,
            "browsed_items": browsed_items
        }
        return JsonResponse(rs_dict)
