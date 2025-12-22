"""
URL configuração do projeto_sad.
"""
from django.contrib import admin
from django.urls import path
from django.urls import include   #<< duda  :) 6
from django.conf import settings    #<< duda  :)  6
from django.conf.urls.static import static  #<< duda  :) 6


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas existentes
    path('simulador/', include('simulador.urls')), #<< duda  :) 6
    path('api/', include('nucleo.urls')),  # LUCIANO aluno 5
    
    # --- NOVAS ROTAS (ADICIONEI AQUI) ---
    path('weka/', include('weka.urls')),                # ALUNO 7 (Módulo Base)
    path('weka-adapter/', include('weka_adapter.urls')), # ALUNO 8 (Classificador)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




