from django.contrib import admin
from .models import Simulacao
from .services import gerar_simulacao_fake
from django.core.files.base import File
from django.conf import settings
import os


class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'cpf_fake', 'idade', 'diagnostico_fake', 'data_criacao')
    actions = ['gerar_simulacao_automatica', 'gerar_lote_10']


    def gerar_simulacao_automatica(self, request, queryset=None):
        """
        Gera 1 simulação usando o service (mesmo da API).
        """

        dados = gerar_simulacao_fake()

        nova = Simulacao(
            nome=dados["nome"],
            cpf_fake=dados["cpf_fake"],
            idade=dados["idade"],
            sintomas=dados["sintomas"],
            diagnostico_fake=dados["diagnostico_fake"],
            confianca=dados["confianca"],
            modo=dados["modo"],
        )
        nova.save()

        # adicionar imagem caso exista
        if dados["imagem_path"]:
            caminho = os.path.join(settings.MEDIA_ROOT, dados["imagem_path"])
            with open(caminho, "rb") as f:
                nome_img = os.path.basename(caminho)
                nova.imagem_escolhida.save(nome_img, File(f), save=True)

        self.message_user(request, " Simulação criada com sucesso!")

    gerar_simulacao_automatica.short_description = "Gerar 1 simulação automaticamente"



    def gerar_lote_10(self, request, queryset=None):
        """
        Cria 10 simulações seguidas (igual ao endpoint /gerar_lote).
        """

        for _ in range(10):
            dados = gerar_simulacao_fake()
            nova = Simulacao(
                nome=dados["nome"],
                cpf_fake=dados["cpf_fake"],
                idade=dados["idade"],
                sintomas=dados["sintomas"],
                diagnostico_fake=dados["diagnostico_fake"],
                confianca=dados["confianca"],
                modo=dados["modo"],
            )
            nova.save()

            if dados["imagem_path"]:
                caminho = os.path.join(settings.MEDIA_ROOT, dados["imagem_path"])
                with open(caminho, "rb") as f:
                    nome_img = os.path.basename(caminho)
                    nova.imagem_escolhida.save(nome_img, File(f), save=True)

        self.message_user(request, " Lote de 10 simulações criado com sucesso!")

    gerar_lote_10.short_description = "Gerar lote (10 simulações)"



admin.site.register(Simulacao, SimulacaoAdmin)

Simulacao._meta.verbose_name = "Simulação"
Simulacao._meta.verbose_name_plural = "Simulações"
