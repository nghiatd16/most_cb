from django.contrib import admin

# Register your models here.
from rest_framework.authtoken.admin import TokenAdmin
from .models import *

TokenAdmin.raw_id_fields = ['user']
admin.site.register(News)
# admin.site.register(Problem)
# admin.site.register(Submission)
# admin.site.register(DraftProblem)