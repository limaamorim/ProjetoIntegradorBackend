"""
URL configuration for projeto_sad project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nucleo.urls')),  # App principal
    path('simulador/', include('simulador.urls')),  # App simulador
    path('weka/', include('weka.urls')),  # App WEKA do aluno 7
    path('weka-adapter/', include('weka_adapter.urls')),  # ⭐ SEU APP!
    path('api/', include('nucleo.urls')),  # API (se necessário)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
