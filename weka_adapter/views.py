from rest_framework.response import Response
from rest_framework.decorators import api_view
from .adapters import WekaAdapter
from .services.report_generator import ReportService # Importando o serviço do Aluno 10
from nucleo.models import PerfilUsuario, AnaliseImagem, ImagemExame # Importando modelos do núcleo
from nucleo.auditoria import audit_log
from django.utils import timezone

@api_view(['GET', 'POST'])
def classificar_imagem(request):

    try:
        # 1. Simulação da IA (Código que você já tem)
        adapter = WekaAdapter()
        resultado_ia = adapter.classificar([]) 

        # 2. Integração com o Banco de Dados (Aluno 10)
        # Em um cenário real, pegaríamos o ID da imagem enviada no request
        # Aqui pegamos a última imagem apenas para exemplo:
        ultima_imagem = ImagemExame.objects.last()
        perfil_medico = PerfilUsuario.objects.get(usuario=request.user)

        # Log de solicitação
        audit_log(
            request=request,
            acao="ANALISE_SOLICITADA",
            recurso="AnaliseImagem",
            detalhe=f"imagem_id={ultima_imagem.id}",
        )
        
        # 3. Criar registro de Análise no Banco
        analise = AnaliseImagem.objects.create(
            imagem=ultima_imagem,
            usuario_solicitante=request.user,
            resultado_classificacao=resultado_ia['classe'],
            score_confianca=resultado_ia['confianca'],
            modelo_versao="Weka J48 v1.0",
            hash_imagem="sha256_exemplo"
        )

        # 4. Chamar o serviço de Geração de Laudo e Impressão (Aluno 9 e 10)
        ip_cliente = request.META.get('REMOTE_ADDR')
        laudo_final = ReportService.gerar_e_registrar(
            analise_obj=analise,
            medico_perfil=perfil_medico,
            ip_cliente=ip_cliente
        )

        # Log de conclusão
        audit_log(
            request=request,
            acao="ANALISE_CONCLUIDA",
            recurso="AnaliseImagem",
            detalhe=f"analise_id={analise.id} resultado={resultado_ia}",
        )

        # Retornamos o resultado da IA e o link para o laudo gerado
        return Response({
            "ia_resultado": resultado_ia,
            "status": "Laudo gerado e registrado para impressão",
            "laudo_id": laudo_final.id
        })

    except Exception as e:

        # Log de exceção
        audit_log(
            request=request,
            acao="ERRO_SISTEMA",
            recurso="AnaliseImagem",
            detalhe=str(e),
        )
        raise
        return Response({"erro": str(e)}, status=500)