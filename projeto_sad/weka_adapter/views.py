from rest_framework.response import Response
from rest_framework.decorators import api_view
from .adapters import WekaAdapter

@api_view(['GET', 'POST']) # Aceita tanto navegador (GET) quanto envio de dados (POST)
def classificar_imagem(request):
    try:
        adapter = WekaAdapter()
        # Passamos uma lista vazia pois é simulação
        resultado = adapter.classificar([]) 
        return Response(resultado)
    except Exception as e:
        return Response({"erro": str(e)}, status=500)

# Desacopla a aplicação principal do motor de IA. Se amanhã trocarmos o Weka por outra tecnologia, só precisamos alterar o código 
# dentro do Adapter, sem quebrar o resto do site!!
