from django.urls import path
from . import views

app_name = 'ia_assistant'

urlpatterns = [
    # Dashboard principal del asistente IA
    path('', views.dashboard_ia_view, name='dashboard'),
    path('chat/', views.chat_ia_view, name='chat'),

    # Consultas IA
    path('consultas/', views.lista_consultas_view, name='lista_consultas'),
    path('consultas/nueva/', views.nueva_consulta_view, name='nueva_consulta'),
    path('consultas/<uuid:pk>/', views.detalle_consulta_view, name='detalle_consulta'),
    path('consultas/<uuid:pk>/feedback/', views.feedback_consulta, name='feedback_consulta'),

    # Predicciones IA
    path('predicciones/', views.lista_predicciones_view, name='lista_predicciones'),
    path('predicciones/<int:pk>/', views.detalle_prediccion_view, name='detalle_prediccion'),
    path('predicciones/generar/', views.generar_predicciones_view, name='generar_predicciones'),

    # Base de conocimiento
    path('conocimiento/', views.base_conocimiento_view, name='base_conocimiento'),
    path('conocimiento/crear/', views.crear_conocimiento_view, name='crear_conocimiento'),
    path('conocimiento/<int:pk>/', views.detalle_conocimiento_view, name='detalle_conocimiento'),
    path('conocimiento/<int:pk>/editar/', views.editar_conocimiento_view, name='editar_conocimiento'),

    # Chat endpoints para AJAX
    path('api/chat/nueva-sesion/', views.nueva_sesion_chat_api, name='api_nueva_sesion_chat'),
    path('api/chat/<uuid:sesion_id>/mensaje/', views.enviar_mensaje_api, name='api_enviar_mensaje'),
    path('api/chat/<uuid:sesion_id>/mensajes/', views.obtener_mensajes_api, name='api_obtener_mensajes'),

    # API endpoints para consultas
    path('api/consulta/', views.procesar_consulta_api, name='api_procesar_consulta'),
    path('api/diagnostico/', views.diagnostico_maquina_api, name='api_diagnostico_maquina'),
    path('api/recomendaciones/<int:maquina_id>/', views.recomendaciones_maquina_api, name='api_recomendaciones'),

    # Análisis de imágenes
    path('api/analizar-imagen/', views.analizar_imagen_api, name='api_analizar_imagen'),

    # Estadísticas y métricas
    path('api/estadisticas/', views.estadisticas_ia_api, name='api_estadisticas'),
    path('api/eficiencia-ia/', views.eficiencia_ia_api, name='api_eficiencia'),
]