# tests/test_integration.py

"""
Testes de integração (end-to-end interno) entre:
- nucleo (CRUD Paciente + upload ImagemExame + auditoria)
- weka_adapter (classificação -> AnaliseImagem -> Laudo + auditoria)

Meta:
- Garantir que o fluxo principal funciona com autenticação
- Garantir que registros no banco são criados
- Garantir que logs de auditoria são registrados com ações corretas
"""

import os
import tempfile
import uuid
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from nucleo.models import (
    Instituicao,
    PerfilUsuario,
    AnaliseImagem,
    Laudo,
    LogAuditoria,
)

# Ajuste caso seu endpoint do Weka esteja diferente
WEKA_CLASSIFICAR_URL = "/weka-adapter/classificar/"


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FluxoCompletoNucleoWekaIntegrationTests(APITestCase):
    """
    Integração completa do fluxo: paciente -> upload -> classificar -> laudo -> logs.
    """

    def setUp(self):
        # Importante: para testes que verificam respostas 500 sem “explodir” a suíte
        self.client.raise_request_exception = False

        # Instituição
        self.inst = Instituicao.objects.create(
            nome_instituicao="Clinica Integração",
            cnpj="12.345.678/0001-99",
        )

        # Usuário + Perfil (MEDICO)
        self.user = User.objects.create_user(
            username="medico_integ",
            password="senha123",
            first_name="Joana",
            last_name="Medeiros",
            email="medico@exemplo.com",
        )
        self.perfil = PerfilUsuario.objects.create(
            usuario=self.user,
            papel="MEDICO",
            ativo=True,
            instituicao=self.inst,
            registro_profissional="CRM-PE 99999",
        )

        # Autentica no client (DRF)
        self.client.force_authenticate(user=self.user)

        # URLs do núcleo (usando os names do seu nucleo/urls.py)
        self.url_paciente_list_create = reverse("paciente-list-create")

    def tearDown(self):
        # Limpa arquivos de teste do MEDIA_ROOT temporário
        for root, _, files in os.walk(TEMP_MEDIA_ROOT, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except OSError:
                    pass

    def _criar_paciente_via_api(self):
        """
        Helper: cria um paciente via API do núcleo e retorna uuid_paciente.
        """
        payload = {
            "nome_completo": "Paciente Integração",
            "cpf": "111.222.333-44",
            "data_nascimento": "2000-01-01",
            "sintomas": "Dor",
            "possivel_diagnostico": "Suspeita",
        }
        resp = self.client.post(self.url_paciente_list_create, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("uuid_paciente", resp.data)
        return resp.data["uuid_paciente"]

    def _upload_imagem_via_api(self, uuid_paciente):
        """
        Helper: faz upload de arquivo no endpoint de upload do núcleo.
        Retorna id da ImagemExame criada.
        """
        url_upload = reverse("upload-imagem-exame", kwargs={"uuid_paciente": uuid_paciente})

        arquivo = SimpleUploadedFile(
            "exame.bin",
            b"fake-bytes",
            content_type="application/octet-stream",
        )

        # Campos obrigatórios do seu serializer/model
        # (paciente vem pela URL e é injetado na view)
        data = {
            "usuario_upload": self.user.id,
            "instituicao": self.inst.id,
            "caminho_arquivo": arquivo,
            "descricao_opcional": "Upload integração",
            "tipo_imagem": "Exame Real",
        }

        resp = self.client.post(url_upload, data, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp.data)
        return resp.data["id"]

    @patch("weka_adapter.views.WekaAdapter.classificar")
    @patch("weka_adapter.views.ReportService.gerar_e_registrar")
    def test_fluxo_completo_cria_analise_laudo_e_logs(
        self,
        mock_gerar_e_registrar,
        mock_classificar,
    ):
        """
        Fluxo:
        - cria paciente (API nucleo)
        - upload imagem (API nucleo)
        - classificar (API weka_adapter)
        Verifica:
        - AnaliseImagem criada e ligada à última imagem
        - Laudo criado (via mock do serviço) e retornado na resposta
        - Logs (UPLOAD_IMAGEM, ANALISE_SOLICITADA, ANALISE_CONCLUIDA) registrados
        """

        # Mock da IA
        mock_classificar.return_value = {
            "classificacao": "Benigno",
            "confianca": 0.95,
            "modelo": "Weka-J48-Mock-v2",
        }

        # Mock do ReportService.gerar_e_registrar para não gerar PDF no teste
        def fake_gerar_e_registrar(analise_obj, medico_perfil, ip_cliente):
            return Laudo.objects.create(
                analise=analise_obj,
                usuario_responsavel=medico_perfil,
                texto_laudo_completo="Laudo teste integração",
                ip_emissao=ip_cliente,
                confirmou_concordancia=True,
                codigo_verificacao=str(uuid.uuid4())[:8],
            )

        mock_gerar_e_registrar.side_effect = fake_gerar_e_registrar

        # 1) cria paciente
        uuid_paciente = self._criar_paciente_via_api()

        # 2) upload imagem
        imagem_id = self._upload_imagem_via_api(uuid_paciente)

        # 3) classifica no endpoint do Weka
        resp = self.client.get(WEKA_CLASSIFICAR_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertIn("laudo_id", resp.data)
        laudo_id = resp.data["laudo_id"]

        # Verifica que análise foi criada para a "última imagem"
        self.assertTrue(AnaliseImagem.objects.filter(imagem_id=imagem_id).exists())
        analise = AnaliseImagem.objects.get(imagem_id=imagem_id)

        # Verifica que laudo existe e aponta para a análise
        self.assertTrue(Laudo.objects.filter(id=laudo_id, analise=analise).exists())

        # Logs esperados
        # Upload: feito na view do núcleo
        self.assertTrue(
            LogAuditoria.objects.filter(
                acao="UPLOAD_IMAGEM",
                recurso="ImagemExame",
            ).exists()
        )

        # Solicitação e conclusão: feitas na view do weka_adapter
        self.assertTrue(
            LogAuditoria.objects.filter(
                acao="ANALISE_SOLICITADA",
                recurso="AnaliseImagem",
            ).exists()
        )
        self.assertTrue(
            LogAuditoria.objects.filter(
                acao="ANALISE_CONCLUIDA",
                recurso="AnaliseImagem",
            ).exists()
        )

    @patch("weka_adapter.views.WekaAdapter.classificar")
    @patch("weka_adapter.views.ReportService.gerar_e_registrar")
    def test_classificar_duas_vezes_mesma_imagem_gera_erro_e_log_erro(
        self,
        mock_gerar_e_registrar,
        mock_classificar,
    ):
        """
        Como AnaliseImagem.imagem é OneToOneField, classificar repetido na mesma imagem
        tende a disparar IntegrityError no create.

        Seu código atual trata exception e retorna 409 + log ERRO_SISTEMA.
        Aqui a gente valida isso sem quebrar a suíte.
        """

        mock_classificar.return_value = {
            "classificacao": "Benigno",
            "confianca": 0.95,
            "modelo": "Weka-J48-Mock-v2",
        }

        # Serviço “leve”
        mock_gerar_e_registrar.side_effect = lambda analise_obj, medico_perfil, ip_cliente: Laudo.objects.create(
            analise=analise_obj,
            usuario_responsavel=medico_perfil,
            texto_laudo_completo="Laudo repetido",
            ip_emissao=ip_cliente,
            confirmou_concordancia=True,
            codigo_verificacao=str(uuid.uuid4())[:8],
        )

        uuid_paciente = self._criar_paciente_via_api()
        imagem_id = self._upload_imagem_via_api(uuid_paciente)

        # 1ª chamada: OK
        resp1 = self.client.get(WEKA_CLASSIFICAR_URL)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertTrue(AnaliseImagem.objects.filter(imagem_id=imagem_id).exists())

        # 2ª chamada: tende a dar 500 (UNIQUE constraint)
        resp2 = self.client.get(WEKA_CLASSIFICAR_URL)
        self.assertEqual(resp2.status_code, status.HTTP_409_CONFLICT)


        # ...

        resp2 = self.client.get(WEKA_CLASSIFICAR_URL)

        # Agora o correto é 409 (conflito) por OneToOne já existente
        self.assertEqual(resp2.status_code, status.HTTP_409_CONFLICT)

        data2 = resp2.json()
        self.assertIn("erro", data2)
        self.assertIn("já possui", data2["erro"].lower())

        # Confirma que logou o erro
        self.assertTrue(
            LogAuditoria.objects.filter(
                acao="ERRO_SISTEMA",
                recurso="AnaliseImagem",
            ).exists()
)