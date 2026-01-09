from django.urls import path
from .views import weka_status

urlpatterns = [
    path('status/', weka_status, name='weka_status'),
]