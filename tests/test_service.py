# tests/test_service.py

"""
Testes unitários da camada de serviço (service layer).

Objetivo:
- Validar o comportamento do ReportService sem depender de Admin/Views
- Garantir que PDF é gerado e salvo no FileField
- Garantir rastreabilidade mínima (registro de impressão quando aplicável)

Observação:
- Esses testes usam banco de testes do Django e um MEDIA_ROOT temporário
  para não poluir o diretório real /media.
"""

import os
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from nucleo.models import (
    Instituicao,
    PerfilUsuario,
    Paciente,
    ImagemExame,
    AnaliseImagem,
    Laudo,
    LaudoImpressao,
)

from weka_adapter.services.report_generator import ReportService


# Cria um MEDIA_ROOT temporário só para o runtime dos testes
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ReportServiceTests(TestCase):
    """
    Testes do ReportService.
    """

    def setUp(self):
        # 1) Instituição
        self.instituicao = Instituicao.objects.create(
            nome_instituicao="Clínica Teste",
            cnpj="12.345.678/0001-99",
        )

        # 2) Usuário (médico)
        self.user = User.objects.create_user(
            username="medico1",
            password="senha-forte",
            first_name="Ana",
            last_name="Silva",
        )

        # 3) Perfil do usuário (RBAC)
        self.perfil_medico = PerfilUsuario.objects.create(
            usuario=self.user,
            papel="MEDICO",
            ativo=True,
            instituicao=self.instituicao,
            registro_profissional="CRM-PE 12345",
        )

        # 4) Paciente
        self.paciente = Paciente.objects.create(
            nome_completo="Paciente Teste",
            cpf="111.222.333-44",
            data_nascimento="2000-01-01",
            sintomas="Dor",
            possivel_diagnostico="Suspeita",
        )

        # 5) Arquivo fake (imagem) para ImagemExame
        # Não precisa ser uma imagem real, só um arquivo válido para FileField.
        self.upload_file = SimpleUploadedFile(
            "exame.bin",
            b"fake-bytes",
            content_type="application/octet-stream",
        )

        # 6) ImagemExame
        self.imagem_exame = ImagemExame.objects.create(
            paciente=self.paciente,
            usuario_upload=self.user,
            instituicao=self.instituicao,
            caminho_arquivo=self.upload_file,
            descricao_opcional="Arquivo teste",
            tipo_imagem="Exame Real",
        )

        # 7) Análise (obrigatória para Laudo)
        self.analise = AnaliseImagem.objects.create(
            imagem=self.imagem_exame,
            usuario_solicitante=self.user,
            resultado_classificacao="Benigno",
            score_confianca="0.950",
            modelo_versao="Mock",
            modelo_checksum="checksum_mock",
            hash_imagem="hash_mock",
        )

    def tearDown(self):
        """
        Limpeza dos arquivos do MEDIA_ROOT temporário.
        (Em Windows, pode falhar se algum handle estiver aberto; em geral o Django fecha.)
        """
        # Remove apenas o que foi criado dentro do MEDIA_ROOT temporário
        # (não remove a pasta raiz TEMP_MEDIA_ROOT por segurança em execuções concorrentes)
        for root, dirs, files in os.walk(TEMP_MEDIA_ROOT, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except OSError:
                    pass

    @patch("weka_adapter.services.report_generator.aplicar_estilo_laudo", autospec=True)
    def test_gerar_pdf_para_laudo_existente_salva_pdf_e_retorna_laudo(self, _mock_estilo):
        """
        Deve gerar um PDF e salvar no campo caminho_pdf.
        Não deve depender de logo existir.
        """
        laudo = Laudo.objects.create(
            analise=self.analise,
            usuario_responsavel=self.perfil_medico,
            texto_laudo_completo="Linha 1\nLinha 2",
            ip_emissao="127.0.0.1",
            confirmou_concordancia=True,
            codigo_verificacao="ABC12345",
        )

        laudo_result = ReportService.gerar_pdf_para_laudo_existente(
            laudo_obj=laudo,
            usuario_solicitante=None,  # sem impressão nesse caso
            ip_cliente="127.0.0.1",
        )

        self.assertEqual(laudo_result.id, laudo.id)

        # O PDF deve ter sido salvo no FileField
        self.assertTrue(laudo_result.caminho_pdf)
        self.assertTrue(os.path.exists(laudo_result.caminho_pdf.path))

        # Validação rápida de “cara de PDF”
        with open(laudo_result.caminho_pdf.path, "rb") as f:
            header = f.read(4)
        self.assertEqual(header, b"%PDF")

        # Sem usuario_solicitante => não cria LaudoImpressao
        self.assertEqual(LaudoImpressao.objects.filter(laudo=laudo).count(), 0)

    @patch("weka_adapter.services.report_generator.aplicar_estilo_laudo", autospec=True)
    def test_gerar_pdf_para_laudo_existente_com_usuario_cria_laudo_impressao(self, _mock_estilo):
        """
        Quando usuario_solicitante é enviado, deve criar LaudoImpressao com IP correto.
        """
        laudo = Laudo.objects.create(
            analise=self.analise,
            usuario_responsavel=self.perfil_medico,
            texto_laudo_completo="Texto de laudo",
            ip_emissao="10.0.0.1",
            confirmou_concordancia=True,
            codigo_verificacao="ZXCV1234",
        )

        ReportService.gerar_pdf_para_laudo_existente(
            laudo_obj=laudo,
            usuario_solicitante=self.user,
            ip_cliente="10.10.10.10",
        )

        imp = LaudoImpressao.objects.filter(laudo=laudo).first()
        self.assertIsNotNone(imp)
        self.assertEqual(imp.usuario, self.user)
        self.assertEqual(imp.ip_origem, "10.10.10.10")

    @patch("weka_adapter.services.report_generator.aplicar_estilo_laudo", autospec=True)
    def test_gerar_e_registrar_cria_laudo_e_pdf(self, _mock_estilo):
        """
        gerar_e_registrar deve:
        - criar um Laudo
        - gerar o PDF e salvar em caminho_pdf
        """
        laudo = ReportService.gerar_e_registrar(
            analise_obj=self.analise,
            medico_perfil=self.perfil_medico,
            ip_cliente="127.0.0.1",
        )

        self.assertIsNotNone(laudo.id)
        self.assertTrue(Laudo.objects.filter(id=laudo.id).exists())

        # PDF gerado e salvo
        self.assertTrue(laudo.caminho_pdf)
        self.assertTrue(os.path.exists(laudo.caminho_pdf.path))

    @patch("weka_adapter.services.report_generator.aplicar_estilo_laudo", autospec=True)
    def test_gerar_e_registrar_nao_cria_laudo_impressao_no_estado_atual(self, _mock_estilo):
        """
        Esse teste evidencia um detalhe do seu código atual:
        gerar_e_registrar() NÃO passa usuario_solicitante para gerar_pdf_para_laudo_existente()
        Logo, hoje não registra LaudoImpressao.

        Se você corrigir o service, esse teste deve ser atualizado/removido.
        """
        laudo = ReportService.gerar_e_registrar(
            analise_obj=self.analise,
            medico_perfil=self.perfil_medico,
            ip_cliente="127.0.0.1",
        )

        self.assertEqual(LaudoImpressao.objects.filter(laudo=laudo).count(), 0)

        # Como corrigir (no seu código, não aqui no teste):
        # return ReportService.gerar_pdf_para_laudo_existente(
        #     novo_laudo,
        #     usuario_solicitante=medico_perfil.usuario,
        #     ip_cliente=ip_cliente
        # )
