from rest_framework import serializers
from .models import Paciente, ImagemExame


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['uuid_paciente', 'nome_completo', 'cpf', 'data_nascimento', 'data_cadastro','sintomas',
            'possivel_diagnostico']
        read_only_fields = ['uuid_paciente', 'data_cadastro']

    def validate(self, attrs):
        # Validação simples ANVISA (nome obrigatório)
        if 'nome_completo' not in attrs or not attrs['nome_completo'].strip():
            raise serializers.ValidationError("O campo 'nome_completo' é obrigatório.")

        return attrs



class ImagemExameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemExame
        fields = [
            'id',
            'paciente',
            'usuario_upload',
            'instituicao',
            'caminho_arquivo',
            'data_upload',
            'descricao_opcional',
            'tipo_imagem'
        ]

