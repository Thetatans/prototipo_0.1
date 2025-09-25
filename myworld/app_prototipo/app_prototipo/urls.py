"""
URL configuration for app_prototipo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import RedirectView

def redirect_to_login(request):
    return redirect('/usuarios/login/')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect root to login
    path('', redirect_to_login, name='home'),

    # App URLs
    path('usuarios/', include('usuarios.urls')),
    path('maquinaria/', include('maquinaria.urls')),
    path('reportes/', include('reportes.urls')),
    path('ia-assistant/', include('ia_assistant.urls')),
    path('documentos/', include('documentos.urls')),
    path('components/', include('components.urls')),

    # API URLs
    path('api/', include('api.urls')),
    path('api/auth/', include('rest_framework.urls')),

    # Status endpoint for system health checks
    path('status/', include('components.status_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'components.views.handler404'
handler500 = 'components.views.handler500'