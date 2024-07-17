from django.urls import re_path

from . import views

urlpatterns = [
    re_path('(?P<submission_id>[0-9]+)/(?P<spam_status>spam|not-spam)/', views.classify, name='classify'),
]
