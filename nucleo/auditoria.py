import logging

logger = logging.getLogger(__name__)

def audit_log(usuario, acao, detalhes=None):
    """
    Registra ações do sistema para auditoria e conformidade (RDC 330).
    """
    mensagem = f"AUDITORIA - Usuário: {usuario} | Ação: {acao} | Detalhes: {detalhes}"
    
    # Imprime no terminal do servidor
    print(mensagem)
    
    # Opcional: Salvar em arquivo de log ou banco de dados
    logger.info(mensagem)