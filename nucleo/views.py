from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging # Importar logging para usar no log provisório

# SERIALIZERS E MODELS DO PACIENTE
from .models import Paciente, ImagemExame
from .serializers import PacienteSerializer, ImagemExameSerializer

# PARA UPLOAD DE ARQUIVOS
from rest_framework.parsers import MultiPartParser, FormParser

# ---  IMPORTAÇÕES PARA INTEGRAÇÃO E AUDITORIA ---
# from nucleo.auditoria import audit_log  <-- COMENTADO POIS O ARQUIVO NÃO EXISTE AINDA
from weka_adapter.integration import processar_analise_automatica 
# ------------------------------------------------------

# --- FUNÇÃO DE AUDITORIA PROVISÓRIA (Para corrigir o erro) ---
def audit_log(request, acao, recurso, detalhe):
    """
    Função temporária para o código não quebrar enquanto
    o arquivo nucleo/auditoria.py não é criado.
    """
    print(f"\n[AUDITORIA] Usuário: {request.user} | Ação: {acao} | Recurso: {recurso}")
    print(f"[DETALHE] {detalhe}\n")
# -------------------------------------------------------------


# LISTAR + CRIAR
class PacienteListCreateView(APIView):
    def get(self, request):
        pacientes = Paciente.objects.all().order_by('-data_cadastro')
        serializer = PacienteSerializer(pacientes, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = PacienteSerializer(data=request.data)
        if serializer.is_valid():
            paciente = serializer.save()
            return Response(PacienteSerializer(paciente).data, status=201)
        return Response(serializer.errors, status=400)


# DETALHE + UPDATE + DELETE
class PacienteDetailView(APIView):
    def get(self, request, uuid_paciente):
        paciente = get_object_or_404(Paciente, uuid_paciente=uuid_paciente)
        serializer = PacienteSerializer(paciente)
        return Response(serializer.data, status=200)

    def put(self, request, uuid_paciente):
        paciente = get_object_or_404(Paciente, uuid_paciente=uuid_paciente)
        serializer = PacienteSerializer(paciente, data=request.data, partial=True)
        if serializer.is_valid():
            paciente = serializer.save()
            return Response(PacienteSerializer(paciente).data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, uuid_paciente):
        paciente = get_object_or_404(Paciente, uuid_paciente=uuid_paciente)
        paciente.delete()
        return Response({"mensagem": "Paciente deletado com sucesso."}, status=204)


# --- [AQUI ESTÁ A GRANDE MUDANÇA] ---
# Substituímos a classe antiga por essa versão "Turbinada"

class UploadImagemExameView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, uuid_paciente):
        # 1. Pega o paciente
        paciente = get_object_or_404(Paciente, uuid_paciente=uuid_paciente)

        # 2. Prepara os dados
        dados = request.data.copy()
        dados['paciente'] = paciente.id

        # Tenta pegar a instituição do médico logado (se não vier na requisição)
        if 'instituicao' not in dados and hasattr(request.user, 'perfilusuario'):
             dados['instituicao'] = request.user.perfilusuario.instituicao.id

        serializer = ImagemExameSerializer(data=dados)

        if serializer.is_valid():
            # 3. SALVA A IMAGEM REAL (Aluno 5)
            # Adicionamos 'usuario_upload' para saber quem mandou
            imagem = serializer.save(usuario_upload=request.user)
            
            # 4. AUDITORIA (Segurança)
            # Agora chama a função definida neste arquivo acima
            audit_log(
                request=request,
                acao="UPLOAD_IMAGEM",
                recurso="ImagemExame",
                detalhe=f"imagem_id={imagem.id} paciente_uuid={paciente.uuid_paciente}",
            )

            # 5. GATILHO DA IA (A mágica da Integração)
            # Aqui chamamos o arquivo que você criou no weka_adapter
            print(f"--- Iniciando análise automática para imagem {imagem.id} ---")
            
            try:
                laudo = processar_analise_automatica(
                    imagem_id=imagem.id,
                    usuario_solicitante=request.user,
                    ip_cliente=request.META.get('REMOTE_ADDR')
                )

                # 6. RESPOSTA TURBINADA
                # Devolvemos os dados da imagem + o resultado da IA na hora!
                resposta = ImagemExameSerializer(imagem).data
                
                if laudo:
                    resposta['status_analise'] = "Concluída com Sucesso"
                    resposta['resultado_ia'] = laudo.analise.resultado_classificacao
                    resposta['confianca_ia'] = laudo.analise.score_confianca
                    resposta['download_laudo'] = laudo.caminho_pdf.url if laudo.caminho_pdf else None
                else:
                    resposta['status_analise'] = "Erro na Análise Automática (Verifique logs)"
            
            except Exception as e:
                # Tratamento de erro caso a integração falhe, para não travar o upload
                print(f"ERRO NA INTEGRAÇÃO: {e}")
                resposta = ImagemExameSerializer(imagem).data
                resposta['status_analise'] = "Falha na integração IA"

            return Response(resposta, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=400)