from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Dashboard
@login_required
def dashboard_view(request):
    return render(request, 'maquinaria/dashboard.html', {'title': 'Dashboard Maquinaria'})

# CRUD de máquinas
@login_required
def lista_maquinas_view(request):
    return render(request, 'maquinaria/lista_maquinas.html', {'title': 'Lista de Máquinas'})

@login_required
def crear_maquina_view(request):
    return render(request, 'maquinaria/crear_maquina.html', {'title': 'Crear Máquina'})

@login_required
def detalle_maquina_view(request, pk):
    return render(request, 'maquinaria/detalle_maquina.html', {'title': 'Detalle Máquina'})

@login_required
def editar_maquina_view(request, pk):
    return render(request, 'maquinaria/editar_maquina.html', {'title': 'Editar Máquina'})

@login_required
def eliminar_maquina_view(request, pk):
    return render(request, 'maquinaria/eliminar_maquina.html', {'title': 'Eliminar Máquina'})

# Estado de máquinas
@login_required
def cambiar_estado_maquina(request, pk):
    return JsonResponse({'success': True})

@login_required
def historial_maquina_view(request, pk):
    return render(request, 'maquinaria/historial_maquina.html', {'title': 'Historial Máquina'})

# Categorías y proveedores
@login_required
def categorias_view(request):
    return render(request, 'maquinaria/categorias.html', {'title': 'Categorías'})

@login_required
def crear_categoria_view(request):
    return render(request, 'maquinaria/crear_categoria.html', {'title': 'Crear Categoría'})

@login_required
def proveedores_view(request):
    return render(request, 'maquinaria/proveedores.html', {'title': 'Proveedores'})

@login_required
def crear_proveedor_view(request):
    return render(request, 'maquinaria/crear_proveedor.html', {'title': 'Crear Proveedor'})

# Alertas
@login_required
def alertas_view(request):
    return render(request, 'maquinaria/alertas.html', {'title': 'Alertas'})

@login_required
def crear_alerta_view(request):
    return render(request, 'maquinaria/crear_alerta.html', {'title': 'Crear Alerta'})

@login_required
def resolver_alerta(request, pk):
    return JsonResponse({'success': True})

@login_required
def detalle_alerta_view(request, pk):
    return render(request, 'maquinaria/detalle_alerta.html', {'title': 'Detalle Alerta'})

# Mantenimiento
@login_required
def mantenimiento_dashboard_view(request):
    return render(request, 'maquinaria/mantenimiento_dashboard.html', {'title': 'Dashboard Mantenimiento'})

@login_required
def programar_mantenimiento_view(request, pk):
    return render(request, 'maquinaria/programar_mantenimiento.html', {'title': 'Programar Mantenimiento'})

# Importar/Exportar
@login_required
def importar_maquinas_view(request):
    return render(request, 'maquinaria/importar_maquinas.html', {'title': 'Importar Máquinas'})

@login_required
def exportar_maquinas_view(request):
    return render(request, 'maquinaria/exportar_maquinas.html', {'title': 'Exportar Máquinas'})

# QR Codes
@login_required
def generar_qr_maquina(request, pk):
    return JsonResponse({'qr_code': 'placeholder'})

@login_required
def info_qr_maquina(request, codigo):
    return render(request, 'maquinaria/info_qr.html', {'title': 'Info QR'})

# API endpoints para AJAX
@login_required
def buscar_maquinas_api(request):
    return JsonResponse({'results': []})

@login_required
def estadisticas_maquinaria_api(request):
    return JsonResponse({'stats': {}})

@login_required
def alertas_activas_api(request):
    return JsonResponse({'alertas': []})

@login_required
def datos_maquina_api(request, pk):
    return JsonResponse({'data': {}})
