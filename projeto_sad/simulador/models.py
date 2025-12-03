from django.db import models

class Simulacao(models.Model):
    nome = models.CharField(max_length=150)
    cpf_fake = models.CharField(max_length=14)
    idade = models.IntegerField()
    sintomas = models.TextField()
    diagnostico_fake = models.CharField(max_length=50)
    confianca = models.FloatField()
    imagem_escolhida = models.FileField(upload_to='simulador_imagens/')
    modo = models.CharField(max_length=20, default='simulado')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulação {self.id} - {self.nome}"
