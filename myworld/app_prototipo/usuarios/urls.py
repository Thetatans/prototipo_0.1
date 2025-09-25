from django.urls import path, include
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Dashboard y home después del login
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),

    # Gestión de usuarios (solo admin)
    path('lista/', views.lista_usuarios_view, name='lista'),
    path('crear/', views.crear_usuario_view, name='crear'),
    path('editar/<int:pk>/', views.editar_usuario_view, name='editar'),
    path('detalle/<int:pk>/', views.detalle_usuario_view, name='detalle'),
    path('cambiar-estado/<int:pk>/', views.cambiar_estado_usuario, name='cambiar_estado'),

    # Configuración
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),

    # API endpoints para AJAX
    path('api/buscar/', views.buscar_usuarios_api, name='api_buscar'),
    path('api/estadisticas/', views.estadisticas_usuarios_api, name='api_estadisticas'),
]