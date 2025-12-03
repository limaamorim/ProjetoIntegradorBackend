import os
import random
from django.conf import settings
from faker import Faker

fake = Faker('pt_BR')

def gerar_simulacao_fake():
    """
    Gera um dicionário com todos os dados necessários
    para criar uma simulação.
    A API vai usar isso.
    O botão no admin também vai usar isso.
    """

    nome = fake.name()
    cpf = fake.cpf()
    idade = random.randint(18, 90)
    sintomas = fake.text(max_nb_chars=200)
    diagnostico = random.choice(['Benigno', 'Maligno', 'Cisto', 'Saudável'])
    confianca = round(random.uniform(0.50, 0.99), 3)

    # Escolhe imagem aleatória
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
