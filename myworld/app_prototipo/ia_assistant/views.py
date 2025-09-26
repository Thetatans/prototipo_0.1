from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
import json
import uuid

@login_required
def dashboard_ia_view(request):
    """Dashboard de IA Assistant con estadísticas simuladas realistas"""
    from datetime import datetime, timedelta
    import random

    # Generar estadísticas simuladas pero realistas
    base_consultas = 156
    consultas_hoy = random.randint(8, 25)
    predicciones_activas = random.randint(12, 30)
    precision_promedio = round(random.uniform(0.85, 0.95), 2)

    # Estadísticas adicionales
    consultas_mes = random.randint(80, 150)
    tiempo_respuesta = round(random.uniform(1.2, 3.5), 1)
    satisfaccion = round(random.uniform(4.0, 4.8), 1)

    # Consultas recientes simuladas
    consultas_recientes = [
        {
            'id': i,
            'pregunta': [
                '¿Cuál es el mantenimiento recomendado para excavadora CAT-320?',
                'Diagnóstico de falla en sistema hidráulico',
                'Predicción de vida útil del motor diesel',
                'Optimización de consumo de combustible',
                'Análisis de vibraciones anómalas'
            ][i % 5],
            'tipo': ['mantenimiento', 'diagnostico', 'prediccion', 'optimizacion', 'analisis'][i % 5],
            'estado': 'completada',
            'confianza': round(random.uniform(0.80, 0.95), 2),
            'timestamp': datetime.now() - timedelta(hours=random.randint(1, 24))
        } for i in range(5)
    ]

    # Predicciones activas simuladas
    predicciones_list = [
        {
            'id': i,
            'maquina': ['EXC-001', 'BUL-002', 'GRU-003', 'CAR-004'][i % 4],
            'tipo': 'Falla predictiva',
            'probabilidad': round(random.uniform(0.15, 0.85), 2),
            'dias_estimados': random.randint(7, 45),
            'criticidad': ['baja', 'media', 'alta'][i % 3]
        } for i in range(6)
    ]

    context = {
        'title': 'Dashboard IA Assistant',
        'total_consultas': base_consultas,
        'consultas_hoy': consultas_hoy,
        'consultas_mes': consultas_mes,
        'predicciones_activas': predicciones_activas,
        'precision_promedio': precision_promedio,
        'tiempo_respuesta': tiempo_respuesta,
        'satisfaccion': satisfaccion,
        'consultas_recientes': consultas_recientes,
        'predicciones_list': predicciones_list,
    }
    return render(request, 'ia_assistant/dashboard_ia.html', context)

@login_required
def chat_ia_view(request):
    return render(request, 'ia_assistant/chat_ia.html', {'title': 'Chat IA Assistant'})

@login_required
def lista_consultas_view(request):
    return render(request, 'ia_assistant/lista_consultas.html', {'title': 'Consultas IA'})

@login_required
def nueva_consulta_view(request):
    return render(request, 'ia_assistant/nueva_consulta.html', {'title': 'Nueva Consulta IA'})

@login_required
def detalle_consulta_view(request, pk):
    return render(request, 'ia_assistant/detalle_consulta.html', {'title': 'Detalle Consulta'})

@login_required
@require_http_methods(["POST"])
def feedback_consulta(request, pk):
    return JsonResponse({'success': True})

@login_required
def lista_predicciones_view(request):
    return render(request, 'ia_assistant/lista_predicciones.html', {'title': 'Predicciones IA'})

@login_required
def detalle_prediccion_view(request, pk):
    return render(request, 'ia_assistant/detalle_prediccion.html', {'title': 'Detalle Predicción'})

@login_required
def generar_predicciones_view(request):
    return render(request, 'ia_assistant/generar_predicciones.html', {'title': 'Generar Predicciones'})

@login_required
def base_conocimiento_view(request):
    return render(request, 'ia_assistant/base_conocimiento.html', {'title': 'Base de Conocimiento'})

@login_required
def crear_conocimiento_view(request):
    return render(request, 'ia_assistant/crear_conocimiento.html', {'title': 'Crear Conocimiento'})

@login_required
def detalle_conocimiento_view(request, pk):
    return render(request, 'ia_assistant/detalle_conocimiento.html', {'title': 'Detalle Conocimiento'})

@login_required
def editar_conocimiento_view(request, pk):
    return render(request, 'ia_assistant/editar_conocimiento.html', {'title': 'Editar Conocimiento'})

@login_required
@require_http_methods(["POST"])
def nueva_sesion_chat_api(request):
    sesion_id = str(uuid.uuid4())
    return JsonResponse({
        'success': True,
        'sesion_id': sesion_id,
        'mensaje': 'Nueva sesión de chat creada'
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def enviar_mensaje_api(request, sesion_id):
    try:
        data = json.loads(request.body)
        mensaje = data.get('mensaje', '')

        # Simular respuesta del IA
        respuesta_ia = f"Gracias por tu consulta: '{mensaje}'. Como asistente IA especializado en maquinaria pesada, puedo ayudarte con diagnósticos, recomendaciones de mantenimiento y predicciones de fallas."

        return JsonResponse({
            'success': True,
            'respuesta': respuesta_ia,
            'timestamp': timezone.now().isoformat(),
            'sesion_id': sesion_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def obtener_mensajes_api(request, sesion_id):
    return JsonResponse({
        'success': True,
        'mensajes': [],
        'sesion_id': sesion_id
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def procesar_consulta_api(request):
    try:
        data = json.loads(request.body)
        consulta = data.get('consulta', '')
        tipo = data.get('tipo', 'general')

        response_data = {
            'success': True,
            'consulta_id': str(uuid.uuid4()),
            'respuesta': f"Procesando consulta de tipo '{tipo}': {consulta}",
            'confianza': 0.85,
            'recomendaciones': [
                'Revisar manual de operación',
                'Verificar niveles de fluidos',
                'Inspeccionar componentes críticos'
            ],
            'timestamp': timezone.now().isoformat()
        }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def diagnostico_maquina_api(request):
    return JsonResponse({
        'success': True,
        'diagnostico': 'Máquina en estado operativo normal',
        'nivel_riesgo': 'bajo',
        'acciones_recomendadas': ['Mantenimiento preventivo programado'],
        'confianza': 0.92
    })

@login_required
def recomendaciones_maquina_api(request, maquina_id):
    return JsonResponse({
        'success': True,
        'maquina_id': maquina_id,
        'recomendaciones': [
            {
                'tipo': 'mantenimiento',
                'descripcion': 'Cambio de aceite programado',
                'prioridad': 'media',
                'fecha_estimada': '2024-02-01'
            },
            {
                'tipo': 'inspección',
                'descripcion': 'Revisión de sistema hidráulico',
                'prioridad': 'alta',
                'fecha_estimada': '2024-01-15'
            }
        ]
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def analizar_imagen_api(request):
    return JsonResponse({
        'success': True,
        'analisis': {
            'descripcion': 'Imagen procesada correctamente',
            'elementos_detectados': ['componente_principal', 'sistema_hidraulico'],
            'estado_general': 'bueno',
            'anomalias': [],
            'confianza': 0.88
        }
    })

@login_required
def estadisticas_ia_api(request):
    return JsonResponse({
        'success': True,
        'estadisticas': {
            'consultas_totales': 156,
            'consultas_mes_actual': 23,
            'precision_promedio': 0.89,
            'tiempo_respuesta_promedio': 2.3,
            'satisfaccion_usuario': 4.2
        }
    })

@login_required
def eficiencia_ia_api(request):
    return JsonResponse({
        'success': True,
        'eficiencia': {
            'predicciones_correctas': 0.87,
            'falsos_positivos': 0.08,
            'falsos_negativos': 0.05,
            'tiempo_procesamiento': 1.8,
            'uso_recursos': 'optimizado'
        }
    })
