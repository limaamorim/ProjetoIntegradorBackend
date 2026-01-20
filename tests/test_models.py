"""
tests/test_models.py

Testes unitários de MODELS do app "nucleo".

Objetivo:
- Provar que os modelos criam registros corretamente
- Validar relacionamentos (FK / OneToOne)
- Validar regras de integridade (ex.: OneToOne único)
- Validar comportamento padrão (auto_now_add, defaults)
- Validar __str__ para evitar "object (1)" no Admin

Como rodar:
    python manage.py test tests.test_models
"""

import uuid

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from nucleo.models import (
    Instituicao,
    PerfilUsuario,
    Paciente,
    ImagemExame,
    AnaliseImagem,
    Laudo,
    HistoricoLaudo,
    LaudoImpressao,
    LogAuditoria,
)


class FactoryMixin:
    """
    Helpers para criação rápida de objetos válidos.
    Evita repetição e deixa o teste mais legível.
    """

    def criar_user(self, username="user1", is_staff=True, is_superuser=False):
        # User do Django (auth_user)
        return User.objects.create_user(
            username=username,
            password="senha123",
            is_staff=is_staff,
            is_superuser=is_superuser,
            first_name="Nome",
            last_name="Sobrenome",
            email=f"{username}@teste.com",
        )

    def criar_instituicao(self, nome="Clínica Teste"):
        # Instituicao tem alguns campos opcionais, mas podemos preencher alguns
        return Instituicao.objects.create(
            nome_instituicao=nome,
            cnpj="12.345.678/0001-90",
            endereco_fisico="Rua A, 100",
            endereco_eletronico="contato@clinica.com",
            telefone="(81) 90000-0000",
        )

    def criar_perfil(self, user, instituicao, papel="MEDICO"):
        # PerfilUsuario exige user + instituicao
        return PerfilUsuario.objects.create(
            usuario=user,
            registro_profissional="CRM-PE 12345",
            papel=papel,
            ativo=True,
            instituicao=instituicao,
        )

    def criar_paciente(self, nome="Maria Silva", cpf="111.222.333-44"):
        # Paciente: nome_completo obrigatório; cpf opcional, mas útil pra teste
        return Paciente.objects.create(
            nome_completo=nome,
            cpf=cpf,
            data_nascimento="1990-01-01",
            sintomas="Dor",
            possivel_diagnostico="Nódulo",
        )

    def criar_imagem_exame(self, paciente, user, instituicao):
        # Para FileField: usamos arquivo fake em memória
        fake_file = SimpleUploadedFile(
            "exame.txt",
            b"conteudo_fake",
            content_type="text/plain",
        )
        return ImagemExame.objects.create(
            paciente=paciente,
            usuario_upload=user,
            instituicao=instituicao,
            caminho_arquivo=fake_file,
            descricao_opcional="Arquivo teste",
            tipo_imagem="Exame Real",
        )

    def criar_analise(self, imagem, user, resultado="Benigno"):
        # AnaliseImagem: modelo_versao, modelo_checksum e hash_imagem são obrigatórios
        return AnaliseImagem.objects.create(
            imagem=imagem,
            usuario_solicitante=user,
            resultado_classificacao=resultado,
            score_confianca=0.876,
            modelo_versao="Weka-J48-Mock-v2",
            modelo_checksum="checksum_teste_123",
            hash_imagem="sha256_fake_123",
        )

    def criar_laudo(self, analise, perfil, codigo="COD-TESTE-1"):
        # Laudo: confirmou_concordancia, ip_emissao e codigo_verificacao são obrigatórios
        return Laudo.objects.create(
            analise=analise,
            usuario_responsavel=perfil,
            texto_laudo_completo="Texto do laudo",
            confirmou_concordancia=True,
            ip_emissao="127.0.0.1",
            laudo_finalizado=False,
            codigo_verificacao=codigo,
        )


class TestModelsBase(TestCase, FactoryMixin):
    """
    Testes base: criação e __str__ de models mais simples.
    """

    def test_instituicao_cria_e_str(self):
        inst = self.criar_instituicao(nome="Hospital UFPE")

        # __str__ deve retornar o nome da instituição
        self.assertEqual(str(inst), "Hospital UFPE")

    def test_perfil_usuario_cria_e_str(self):
        user = self.criar_user(username="medico1")
        inst = self.criar_instituicao()
        perfil = self.criar_perfil(user=user, instituicao=inst, papel="MEDICO")

        # Verifica relacionamentos
        self.assertEqual(perfil.usuario, user)
        self.assertEqual(perfil.instituicao, inst)

        # __str__ deve incluir username ou nome e o papel
        self.assertIn("MEDICO", str(perfil))

    def test_paciente_cria_uuid_e_str(self):
        paciente = self.criar_paciente()

        # uuid_paciente deve existir e ser UUID
        self.assertIsNotNone(paciente.uuid_paciente)
        self.assertIsInstance(paciente.uuid_paciente, uuid.UUID)

        # data_cadastro auto_now_add deve preencher
        self.assertIsNotNone(paciente.data_cadastro)

        # __str__ retorna nome
        self.assertIn("Maria", str(paciente))



    """
    Testes para LogAuditoria:
    - cria registro
    - valida default protegido=True
    - valida que acao aceita uma opção válida
    """

    def test_log_auditoria_cria(self):
        user = self.criar_user(username="auditor1")

        log = LogAuditoria.objects.create(
            usuario=user,
            acao="PACIENTE_CRIADO",
            recurso="Paciente",
            detalhe="CRIACAO paciente_uuid=xxxx",
            ip_origem="127.0.0.1",
        )

        # data_hora auto_now_add deve preencher
        self.assertIsNotNone(log.data_hora)

        # default protegido=True
        self.assertTrue(log.protegido)

        self.assertEqual(log.usuario, user)
        self.assertEqual(log.acao, "PACIENTE_CRIADO")
        self.assertEqual(log.recurso, "Paciente")
        self.assertEqual(log.ip_origem, "127.0.0.1")

    def test_log_auditoria_acao_invalida_falha_no_full_clean(self):
        """
        Observação:
        O Django NÃO valida choices automaticamente no .save() em nível de modelo.
        Para validar choices em testes, usamos full_clean().
        Isso simula validação "de formulário/serializer".
        """
        user = self.criar_user(username="auditor2")

        log = LogAuditoria(
            usuario=user,
            acao="ACAO_INEXISTENTE",
            recurso="Teste",
            detalhe="x",
            ip_origem="127.0.0.1",
        )

        with self.assertRaises(Exception):
            log.full_clean()