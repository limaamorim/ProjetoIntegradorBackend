
from django.urls import path
from .views import gerar_simulacao_api, listar_simulacoes, detalhar_simulacao

urlpatterns = [
    path("gerar/", gerar_simulacao_api, name="gerar_simulacao_api"),
    path("listar/", listar_simulacoes, name="listar_simulacoes"),
    path("detalhar/<int:id>/", detalhar_simulacao, name="detalhar_simulacao"),
]
