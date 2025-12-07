
from django.urls import path
from .views import ClassifyImageView, WekaStatusView

urlpatterns = [
    path('classify/', ClassifyImageView.as_view(), name='classify_image'),
    path('status/', WekaStatusView.as_view(), name='weka_status'),
    path('', WekaStatusView.as_view(), name='weka_adapter_home'),
]
