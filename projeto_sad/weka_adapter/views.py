
from django.urls import path
from .views import ClassifyImageView, BatchClassificationView, WekaToolsView

urlpatterns = [
    path('classify/', ClassifyImageView.as_view(), name='classify_image'),
    path('batch/', BatchClassificationView.as_view(), name='batch_classification'),
    path('tools/', WekaToolsView.as_view(), name='weka_tools'),
    path('tools/<str:tool>/', WekaToolsView.as_view(), name='weka_tool_detail'),
    path('', ClassifyImageView.as_view(), name='weka_adapter_home'),
]
