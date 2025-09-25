from django.urls import path
from . import views

app_name = 'components'

urlpatterns = [
    # Componentes de UI reutilizables
    path('', views.components_view, name='components'),
    path('widgets/', views.widgets_view, name='widgets'),
    path('widgets/<int:pk>/', views.detalle_widget_view, name='detalle_widget'),
    path('ui-components/', views.ui_components_view, name='ui_components'),

    # Sistema de búsqueda
    path('busqueda/', views.busqueda_avanzada_view, name='busqueda_avanzada'),
    path('busqueda/inteligente/', views.busqueda_inteligente_view, name='busqueda_inteligente'),

    # Sistema de ayuda
    path('ayuda/', views.sistema_ayuda_view, name='sistema_ayuda'),
    path('ayuda/contextual/', views.ayuda_contextual_view, name='ayuda_contextual'),

    # Notificaciones
    path('notificaciones/', views.lista_notificaciones_view, name='lista_notificaciones'),
    path('notificaciones/marcar-leida/<uuid:pk>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/archivar/<uuid:pk>/', views.archivar_notificacion, name='archivar_notificacion'),

    # Configuración del sistema
    path('configuracion/', views.configuracion_sistema_view, name='configuracion_sistema'),
    path('configuracion/crear/', views.crear_configuracion_view, name='crear_configuracion'),
    path('configuracion/<int:pk>/editar/', views.editar_configuracion_view, name='editar_configuracion'),

    # Logs del sistema
    path('logs/', views.logs_sistema_view, name='logs_sistema'),
    path('logs/exportar/', views.exportar_logs_view, name='exportar_logs'),

    # Menús personalizados
    path('menus/', views.menus_personalizados_view, name='menus_personalizados'),
    path('menus/crear/', views.crear_menu_personalizado_view, name='crear_menu_personalizado'),
    path('menus/<int:pk>/eliminar/', views.eliminar_menu_personalizado, name='eliminar_menu_personalizado'),

    # API endpoints para componentes dinámicos
    path('api/notificaciones/', views.notificaciones_api, name='api_notificaciones'),
    path('api/notificaciones/count/', views.count_notificaciones_api, name='api_count_notificaciones'),
    path('api/buscar/', views.busqueda_global_api, name='api_busqueda_global'),
    path('api/ayuda/<str:seccion>/', views.ayuda_contextual_api, name='api_ayuda_contextual'),

    # Sistema de salud del sistema
    path('api/health/', views.health_check_api, name='api_health_check'),
    path('api/version/', views.version_api, name='api_version'),

    # Dashboard widgets data
    path('api/widget/<int:widget_id>/actualizar/', views.actualizar_widget_api, name='api_actualizar_widget'),
]