from django.contrib import admin
from .models import Simulacao
from .services import gerar_simulacao_fake
from django.core.files.base import File
from django.conf import settings
import os

class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'cpf_fake', 'idade', 'diagnostico_fake', 'data_criacao')
    actions = ['gerar_simulacao_automatica']

    def gerar_simulacao_automatica(self, request, queryset=None):
        """
        Chama o serviço que cria os dados fake
        e salva uma nova simulação automaticamente.
        """

        dados = gerar_simulacao_fake()

        nova_simulacao = Simulacao(
            nome = dados["nome"],
            cpf_fake = dados["cpf_fake"],
            idade = dados["idade"],
            sintomas = dados["sintomas"],
            diagnostico_fake = dados["diagnostico_fake"],
            confianca = dados["confianca"],
            modo = dados["modo"],
        )

        # salvar primeiro para ter ID
        nova_simulacao.save()

        # se tiver imagem, anexar ao FileField
        if dados["imagem_path"]:
            caminho = os.path.join(settings.MEDIA_ROOT, dados["imagem_path"])
            with open(caminho, "rb") as f:
                nome_img = os.path.basename(caminho)
                nova_simulacao.imagem_escolhida.save(nome_img, File(f), save=True)

        self.message_user(request, "Simulação criada com sucesso!")

    gerar_simulacao_automatica.short_description = "Gerar simulação automaticamente"

admin.site.register(Simulacao, SimulacaoAdmin)


Simulacao._meta.verbose_name = "Simulação"
Simulacao._meta.verbose_name_plural = "Simulações"

