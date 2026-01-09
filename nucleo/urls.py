from django.urls import path
from .views import PacienteListCreateView, PacienteDetailView
from .views import UploadImagemExameView


urlpatterns = [
    path('pacientes/', PacienteListCreateView.as_view(), name='paciente-list-create'),
    path('pacientes/<uuid:uuid_paciente>/', PacienteDetailView.as_view(), name='paciente-detail'),
    
    path('pacientes/<uuid:uuid_paciente>/upload-imagem/', 
         UploadImagemExameView.as_view(), 
         name='upload-imagem-exame'),

]
