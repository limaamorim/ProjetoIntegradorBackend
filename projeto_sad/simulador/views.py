from rest_framework.response import Response
from rest_framework.decorators import api_view
from .services import gerar_simulacao_fake
from .models import Simulacao
from django.core.files.base import File
from django.conf import settings
import os


@api_view(["GET", "POST"])
def gerar_simulacao_api(request):
    """
    Endpoint que cria uma simulação fake e retorna os dados em JSON.
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

    # anexar imagem se houver
    if dados["imagem_path"]:
        caminho = os.path.join(settings.MEDIA_ROOT, dados["imagem_path"])
        with open(caminho, "rb") as f:
            nome_img = os.path.basename(caminho)
            nova.imagem_escolhida.save(nome_img, File(f), save=True)

    return Response({
        "id": nova.id,
        "nome": nova.nome,
        "cpf_fake": nova.cpf_fake,
        "idade": nova.idade,
        "sintomas": nova.sintomas,
        "diagnostico_fake": nova.diagnostico_fake,
        "confianca": nova.confianca,
        "imagem_url": nova.imagem_escolhida.url if nova.imagem_escolhida else None,
        "modo": nova.modo,
        "data_criacao": nova.data_criacao,
    })

@api_view(["GET"])
def listar_simulacoes(request):
    """
    Endpoint que lista todas as simulações existentes.
    Retorna uma lista em JSON.
    """
    dados = []

    for s in Simulacao.objects.all().order_by("-id"):

        imagem_url = None
        if hasattr(s, "imagem_escolhida") and s.imagem_escolhida:
            try:
                imagem_url = s.imagem_escolhida.url
            except:
                imagem_url = None

        dados.append({
            "id": s.id,
            "nome": s.nome,
            "cpf_fake": s.cpf_fake,
            "idade": s.idade,
            "diagnostico_fake": s.diagnostico_fake,
            "confianca": s.confianca,
            "imagem_url": imagem_url,
            "modo": s.modo,
            "data_criacao": s.data_criacao,
        })

    return Response(dados)

@api_view(["GET"])
def detalhar_simulacao(request, id):
    """
    Endpoint que retorna uma simulação específica pelo ID.
    """
    try:
        sim = Simulacao.objects.get(id=id)
    except Simulacao.DoesNotExist:
        return Response({"erro": "Simulação não encontrada."}, status=404)

    imagem_url = None
    if sim.imagem_escolhida:
        imagem_url = request.build_absolute_uri(sim.imagem_escolhida.url)

    dados = {
        "id": sim.id,
        "nome": sim.nome,
        "cpf_fake": sim.cpf_fake,
        "idade": sim.idade,
        "sintomas": sim.sintomas,
        "diagnostico_fake": sim.diagnostico_fake,
        "confianca": sim.confianca,
        "imagem_url": imagem_url,
        "modo": sim.modo,
        "data_criacao": sim.data_criacao,
    }

    return Response(dados)
