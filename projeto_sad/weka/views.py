from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET']) #Diz que essa função só aceita pedidos de leitura (GET)
def weka_status(request):
    """
    View simples para provar que o app WEKA existe e está integrado.
    """
    return Response({
        "modulo": "WEKA (Core)", # Identifica quem está falando
        "status": "Online",      # Diz que está tudo bem
        "msg": "Módulo base do Weka carregado com sucesso." # Mensagem para humanos
    })

# Isola o núcleo do Weka. Criado um endpoint de status para garantir a observabilidade do sistema. Se o Weka cair, se descobre por aqui!!!