from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include  

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adicione aqui as urls dos seus apps, por exemplo:
    # path('', include('nucleo.urls')),
    path('simulador/', include('simulador.urls')), #<< duda  :) 6
    path('api/', include('nucleo.urls')),  # LUCIANO aluno 5
    
]

# Serve arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
