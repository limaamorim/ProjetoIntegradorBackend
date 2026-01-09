
from django.urls import path
from .views import gerar_simulacao_api, listar_simulacoes, detalhar_simulacao, gerar_lote, gerar_lote_arff

urlpatterns = [
    path("gerar/", gerar_simulacao_api, name="gerar_simulacao_api"),
    path("listar/", listar_simulacoes, name="listar_simulacoes"),
    path("detalhar/<int:id>/", detalhar_simulacao, name="detalhar_simulacao"),
    path("gerar_lote/", gerar_lote, name = "gerar_lote"),
    path("lote_arff/", gerar_lote_arff, name = "gerar_lote_arff"),

]
