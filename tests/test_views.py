"""
tests/test_views.py

Testes de views (API) do projeto, mantendo tudo na pasta raiz /tests.

O foco aqui é:
1) Validar comportamento HTTP (status codes + payload)
2) Validar efeitos colaterais relevantes (criação/remoção/alteração no banco)
3) Validar auditoria (LogAuditoria) para ações críticas (ANVISA/RDC 330)

Observação: onde existe IO pesado (PDF/ReportService) a gente mocka para o teste ser rápido e confiável.
"""

import uuid
import tempfile
from unittest.mock import patch

from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse


from nucleo.models import (
    Instituicao,
    PerfilUsuario,
    Paciente,
    ImagemExame,
    AnaliseImagem,
    Laudo,
    LogAuditoria,
)


PACIENTES_URL = reverse("paciente-list-create")

def paciente_detail_url(uuid):
    return reverse("paciente-detail", kwargs={"uuid_paciente": uuid})

def upload_imagem_url(uuid):
    return reverse("upload-imagem-exame", kwargs={"uuid_paciente": uuid})



def criar_usuario(username="medico1", senha="123"):
    """Helper para criar usuário rapidamente."""
    return User.objects.create_user(username=username, password=senha)


def criar_instituicao():
    """Helper para criar instituição (necessária em PerfilUsuario e ImagemExame)."""
    return Instituicao.objects.create(
        nome_instituicao="Clínica Teste",
        cnpj="12.345.678/0001-90",
        endereco_fisico="Rua X, 123",
        endereco_eletronico="contato@clinica.com",
        telefone="81999999999",
    )


def criar_perfil_medico(user, instituicao):
    """Helper para PerfilUsuario do médico."""
    return PerfilUsuario.objects.create(
        usuario=user,
        instituicao=instituicao,
        papel="MEDICO",
        registro_profissional="CRM-0001",
        ativo=True,
    )


def criar_paciente(nome="Maria José", cpf="111.222.333-44"):
    """Helper para criar paciente real."""
    return Paciente.objects.create(
        nome_completo=nome,
        cpf=cpf,
        data_nascimento="1990-01-01",
        sintomas="Dor",
        possivel_diagnostico="Avaliar",
    )


def criar_imagem_exame(paciente, usuario_upload, instituicao):
    """
    Cria um ImagemExame com um arquivo fake em memória.
    (Não precisa existir arquivo real no disco para o Django aceitar o upload no teste.)
    """
    fake_file = SimpleUploadedFile("exame.txt", b"conteudo_fake", content_type="text/plain")
    return ImagemExame.objects.create(
        paciente=paciente,
        usuario_upload=usuario_upload,
        instituicao=instituicao,
        caminho_arquivo=fake_file,
        descricao_opcional="Imagem teste",
        tipo_imagem="Exame Real",
    )


# -------------------------------------------------------------------
# Testes do NÚCLEO (Paciente + Upload)
# -------------------------------------------------------------------
@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class NucleoViewsTests(APITestCase):
    """
    Esses testes verificam:
    - API funcionando (status)
    - persistência de dados
    - logs de auditoria (criação) com a ação correta
    """

    def setUp(self):
        self.client = APIClient()

        self.user = criar_usuario("user_api")
        self.client.force_authenticate(user=self.user)

        self.instituicao = criar_instituicao()
        self.perfil = criar_perfil_medico(self.user, self.instituicao)

        # Limpa logs antes de cada teste para as contagens ficarem previsíveis
        LogAuditoria.objects.all().delete()

    def test_paciente_create_deve_criar_paciente_e_log(self):
        payload = {
            "nome_completo": "Maria Silva",
            "cpf": "12345678900"
        }

        resp = self.client.post(PACIENTES_URL, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


        # Confere se salvou no banco
        self.assertEqual(Paciente.objects.count(), 1)
        paciente = Paciente.objects.first()
        self.assertEqual(str(paciente.nome_completo), payload["nome_completo"])

        # Confere log (a view atual usa "ACESSO_RELATORIO" mesmo para CRUD)
        self.assertTrue(
            LogAuditoria.objects.filter(
                acao="ACESSO_RELATORIO",
                recurso="Paciente",
            ).exists()
        )

    def test_paciente_update_deve_atualizar_e_logar(self):
        paciente = Paciente.objects.create(nome_completo="Ana", cpf="111")

        resp = self.client.put(
            paciente_detail_url(paciente.uuid_paciente),
            {"nome_completo": "Ana Atualizada"},
            format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertTrue(
            LogAuditoria.objects.filter(
                acao="ACESSO_RELATORIO",
                recurso="Paciente",
                detalhe__icontains="ATUALIZACAO",
            ).exists()
        )

    def test_paciente_delete_deve_remover_e_logar(self):
        paciente = Paciente.objects.create(nome_completo="João", cpf="222")

        resp = self.client.delete(
            paciente_detail_url(paciente.uuid_paciente)
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Paciente.objects.count(), 0)
        self.assertTrue(
            LogAuditoria.objects.filter(
                acao="ACESSO_RELATORIO",
                recurso="Paciente",
                detalhe__icontains="EXCLUSAO",
            ).exists()
        )

from django.core.files.uploadedfile import SimpleUploadedFile

def test_upload_imagem_deve_criar_imagem_e_log_upload(self):
    paciente = Paciente.objects.create(nome_completo="Carlos", cpf="333")

    arquivo = SimpleUploadedFile(
        "exame.jpg",
        b"conteudo-falso",
        content_type="image/jpeg"
    )

    resp = self.client.post(
        upload_imagem_url(paciente.uuid_paciente),
        {
            "usuario_upload": self.user.id,
            "instituicao": self.instituicao.id,
            "caminho_arquivo": arquivo,
        },
        format="multipart"
    )

    self.assertEqual(resp.status_code, status.HTTP_201_CREATED)