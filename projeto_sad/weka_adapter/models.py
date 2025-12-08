"""
weka_adapter/models.py
Modelos de dados para armazenar resultados de classificação
"""
from django.db import models
from django.utils import timezone
import uuid


class ClassificationResult(models.Model):
    """
    Modelo para armazenar resultados de classificação.
    """
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]
    
    # Class choices
    CLASS_CHOICES = [
        ('NORMAL', 'Normal'),
        ('BENIGNO', 'Benigno'),
        ('CISTO', 'Cisto'),
        ('MALIGNO', 'Maligno'),
    ]
    
    # Campos principais
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255, blank=True)
    file_path = models.TextField(blank=True)
    
    # Resultados da classificação
    predicted_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    confidence = models.FloatField()  # 0.0 a 1.0
    confidence_percentage = models.FloatField()  # 0.0 a 100.0
    
    # Distribuição de probabilidades (armazenada como JSON)
    distribution = models.JSONField(default=dict)
    
    # Metadados
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    weka_mode = models.CharField(max_length=20, default='real')  # 'real' ou 'simulated'
    processing_time = models.FloatField(default=0.0)  # em segundos
    features_extracted = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(default=timezone.now)
    
    # Campos para diagnóstico
    diagnosis_report = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # Dados do sistema
    system_status = models.JSONField(default=dict, blank=True)
    weka_version = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Resultado de Classificação'
        verbose_name_plural = 'Resultados de Classificação'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['predicted_class']),
            models.Index(fields=['confidence_percentage']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.predicted_class} ({self.confidence_percentage}%)"
    
    def get_confidence_display(self):
        """Retorna a confiança formatada como porcentagem."""
        return f"{self.confidence_percentage:.1f}%"
    
    def is_high_confidence(self):
        """Verifica se é uma classificação de alta confiança."""
        return self.confidence_percentage >= 80.0
    
    def is_critical_case(self):
        """Verifica se é um caso crítico (maligno com alta confiança)."""
        return self.predicted_class == 'MALIGNO' and self.confidence_percentage >= 70.0


class BatchClassification(models.Model):
    """
    Modelo para armazenar classificações em lote.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_name = models.CharField(max_length=255, default="Lote sem nome")
    
    # Estatísticas
    total_images = models.IntegerField(default=0)
    successful_classifications = models.IntegerField(default=0)
    failed_classifications = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    # Resultados consolidados
    class_distribution = models.JSONField(default=dict)
    class_percentages = models.JSONField(default=dict)
    average_confidence = models.FloatField(default=0.0)
    
    # Relacionamentos
    classification_results = models.ManyToManyField(
        ClassificationResult, 
        related_name='batches',
        blank=True
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(default=timezone.now)
    consolidated_report = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Classificação em Lote'
        verbose_name_plural = 'Classificações em Lote'
    
    def __str__(self):
        return f"{self.batch_name} - {self.total_images} imagens"
    
    def get_success_rate_display(self):
        """Retorna a taxa de sucesso formatada."""
        return f"{self.success_rate:.1f}%"


# Modelo para histórico do sistema WEKA
class WekaSystemLog(models.Model):
    """
    Modelo para armazenar logs do sistema WEKA.
    """
    LOG_LEVEL_CHOICES = [
        ('INFO', 'Informação'),
        ('WARNING', 'Aviso'),
        ('ERROR', 'Erro'),
        ('DEBUG', 'Depuração'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES)
    message = models.TextField()
    component = models.CharField(max_length=50, default='weka_adapter')
    
    # Dados contextuais
    data = models.JSONField(default=dict, blank=True)
    exception_traceback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log do Sistema WEKA'
        verbose_name_plural = 'Logs do Sistema WEKA'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.timestamp}: {self.message[:100]}"
