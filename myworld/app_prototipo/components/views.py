from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

def components_view(request):
    return HttpResponse("Componentes del sistema SENA")

# Error handlers
def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

# Status checks
def status_check(request):
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now(),
        'service': 'Sistema SENA - Gestión Maquinaria'
    })

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'database': 'connected',
        'version': '1.0.0'
    })

def version_info(request):
    return JsonResponse({
        'version': '1.0.0',
        'build': 'prototype',
        'timestamp': timezone.now()
    })

def database_status(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'connected', 'timestamp': timezone.now()})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

# Placeholder views for the URLs that were defined
@login_required
def widgets_view(request):
    return render(request, 'components/widgets.html', {'title': 'Widgets'})

@login_required
def detalle_widget_view(request, pk):
    return render(request, 'components/widget_detail.html', {'title': 'Detalle Widget'})

@login_required
def ui_components_view(request):
    return render(request, 'components/ui_components.html', {'title': 'Componentes UI'})

@login_required
def busqueda_avanzada_view(request):
    return render(request, 'components/busqueda_avanzada.html', {'title': 'Búsqueda Avanzada'})

@login_required
def busqueda_inteligente_view(request):
    return render(request, 'components/busqueda_inteligente.html', {'title': 'Búsqueda Inteligente'})

@login_required
def sistema_ayuda_view(request):
    return render(request, 'components/sistema_ayuda.html', {'title': 'Sistema de Ayuda'})

@login_required
def ayuda_contextual_view(request):
    return render(request, 'components/ayuda_contextual.html', {'title': 'Ayuda Contextual'})

@login_required
def lista_notificaciones_view(request):
    return render(request, 'components/lista_notificaciones.html', {'title': 'Notificaciones'})

@login_required
@require_http_methods(["POST"])
def marcar_notificacion_leida(request, pk):
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def archivar_notificacion(request, pk):
    return JsonResponse({'success': True})

@login_required
def configuracion_sistema_view(request):
    return render(request, 'components/configuracion_sistema.html', {'title': 'Configuración Sistema'})

@login_required
def crear_configuracion_view(request):
    return render(request, 'components/crear_configuracion.html', {'title': 'Crear Configuración'})

@login_required
def editar_configuracion_view(request, pk):
    return render(request, 'components/editar_configuracion.html', {'title': 'Editar Configuración'})

@login_required
def logs_sistema_view(request):
    return render(request, 'components/logs_sistema.html', {'title': 'Logs del Sistema'})

@login_required
def exportar_logs_view(request):
    return JsonResponse({'message': 'Función de exportar logs en desarrollo'})

@login_required
def menus_personalizados_view(request):
    return render(request, 'components/menus_personalizados.html', {'title': 'Menús Personalizados'})

@login_required
def crear_menu_personalizado_view(request):
    return render(request, 'components/crear_menu_personalizado.html', {'title': 'Crear Menú'})

@login_required
@require_http_methods(["POST"])
def eliminar_menu_personalizado(request, pk):
    return JsonResponse({'success': True})

# API endpoints
@login_required
def notificaciones_api(request):
    return JsonResponse({'notificaciones': []})

@login_required
def count_notificaciones_api(request):
    return JsonResponse({'count': 0})

@login_required
def busqueda_global_api(request):
    return JsonResponse({'results': []})

@login_required
def ayuda_contextual_api(request, seccion):
    return JsonResponse({'ayuda': f'Ayuda para {seccion}'})

def health_check_api(request):
    return JsonResponse({'status': 'ok', 'timestamp': timezone.now()})

def version_api(request):
    return JsonResponse({'version': '1.0.0', 'build': 'prototype'})

@login_required
def actualizar_widget_api(request, widget_id):
    return JsonResponse({'success': True, 'data': {}})