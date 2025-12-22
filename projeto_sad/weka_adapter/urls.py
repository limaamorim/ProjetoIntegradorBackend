from django.urls import path
from .views import classificar_imagem

urlpatterns = [
    path('classificar/', classificar_imagem, name='classificar_imagem'),
]