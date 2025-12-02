from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

# SERIALIZERS E MODELS DO PACIENTE
from .models import Paciente, ImagemExame
from .serializers import PacienteSerializer, ImagemExameSerializer

# PARA UPLOAD DE ARQUIVOS
from rest_framework.parsers import MultiPartParser, FormParser


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

class UploadImagemExameView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, uuid_paciente):
        paciente = get_object_or_404(Paciente, uuid_paciente=uuid_paciente)

        dados = request.data.copy()
        dados['paciente'] = paciente.id

        serializer = ImagemExameSerializer(data=dados)

        if serializer.is_valid():
            imagem = serializer.save()
            return Response(
                ImagemExameSerializer(imagem).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)
