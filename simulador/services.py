import os
import random
from django.conf import settings
from faker import Faker

fake = Faker('pt_BR')

def gerar_simulacao_fake():
    """
    Gera um dicionário coerente para criar uma simulação.
    Mantém exatamente os mesmos campos usados no projeto,
    sem modificar models, serializers ou views de terceiros.
    """

    nome = fake.name()
    cpf = fake.cpf()
    idade = random.randint(18, 90)

    # ----------------------------------------
    # 1) SINTOMAS COERENTES
    # ----------------------------------------
    sintomas_possiveis = [
        "dor localizada",
        "aumento de temperatura",
        "região rígida",
        "formigamento leve",
        "sensibilidade ao toque",
        "desconforto mamário",
        "sem sintomas aparentes"
    ]

    # Seleciona de 1 a 3 sintomas
    sintomas_escolhidos = random.sample(sintomas_possiveis, k=random.randint(1, 3))

    # Garantir que "sem sintomas aparentes" NÃO venha junto de outros sintomas
    if "sem sintomas aparentes" in sintomas_escolhidos and len(sintomas_escolhidos) > 1:
        sintomas_escolhidos = ["sem sintomas aparentes"]

    sintomas = ", ".join(sintomas_escolhidos)

    # ----------------------------------------
    # 2) DIAGNÓSTICO FAKE COERENTE
    # ----------------------------------------
    if sintomas == "sem sintomas aparentes":
        diagnostico = "SAUDÁVEL"

    elif "aumento de temperatura" in sintomas and "região rígida" in sintomas:
        diagnostico = "MALIGNO"

    elif "região rígida" in sintomas or "sensibilidade ao toque" in sintomas:
        diagnostico = "BENIGNO"

    elif "dor localizada" in sintomas:
        diagnostico = "CISTO"

    else:
        diagnostico = "INCONCLUSIVO"

    # ----------------------------------------
    # 3) CONFIANÇA — AJUSTADA PARA 0.70 A 0.99 (como pedido)
    # ----------------------------------------
    confianca = round(random.uniform(0.70, 0.99), 3)

    # ----------------------------------------
    # 4) IMAGEM
    # ----------------------------------------
    pasta_imagens = os.path.join(settings.MEDIA_ROOT, 'termografias')
    imagens = [
        f for f in os.listdir(pasta_imagens)
        if f.lower().endswith(('.jpg', '.jpeg'))
    ]

    imagem_escolhida = random.choice(imagens) if imagens else None

    return {
        "nome": nome,
        "cpf_fake": cpf,
        "idade": idade,
        "sintomas": sintomas,
        "diagnostico_fake": diagnostico,
        "confianca": confianca,
        "imagem_path": f"termografias/{imagem_escolhida}" if imagem_escolhida else None,
        "modo": "simulado"
    }
