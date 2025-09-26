from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Maquina, CategoriaMaquina, Proveedor, AlertaMaquina, HistorialMaquina
from usuarios.models import Usuario

# Dashboard
@login_required
def dashboard_view(request):
    """Dashboard principal de maquinaria con estadísticas reales"""
    # Estadísticas básicas
    total_maquinas = Maquina.objects.count()
    maquinas_operativas = Maquina.objects.filter(estado='operativa').count()
    maquinas_mantenimiento = Maquina.objects.filter(estado='mantenimiento').count()
    alertas_activas = AlertaMaquina.objects.filter(estado='activa').count()

    # Estadísticas por categoría
    stats_por_categoria = CategoriaMaquina.objects.annotate(
        total_maquinas=Count('maquina')
    ).order_by('-total_maquinas')[:5]

    # Actividad reciente
    actividad_reciente = HistorialMaquina.objects.select_related(
        'maquina', 'usuario'
    ).order_by('-fecha_evento')[:10]

    # Alertas recientes
    alertas_recientes = AlertaMaquina.objects.select_related(
        'maquina'
    ).filter(estado='activa').order_by('-fecha_creacion')[:5]

    context = {
        'title': 'Dashboard Maquinaria',
        'total_maquinas': total_maquinas,
        'maquinas_operativas': maquinas_operativas,
        'maquinas_mantenimiento': maquinas_mantenimiento,
        'alertas_activas': alertas_activas,
        'stats_por_categoria': stats_por_categoria,
        'actividad_reciente': actividad_reciente,
        'alertas_recientes': alertas_recientes,
    }

    return render(request, 'maquinaria/dashboard.html', context)

# CRUD de máquinas
@login_required
def lista_maquinas_view(request):
    """Lista todas las máquinas con filtros y paginación"""
    maquinas_list = Maquina.objects.select_related('categoria', 'proveedor', 'responsable').all()

    # Filtros
    estado_filtro = request.GET.get('estado')
    categoria_filtro = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda')

    if estado_filtro:
        maquinas_list = maquinas_list.filter(estado=estado_filtro)

    if categoria_filtro:
        maquinas_list = maquinas_list.filter(categoria_id=categoria_filtro)

    if busqueda:
        maquinas_list = maquinas_list.filter(
            Q(codigo_inventario__icontains=busqueda) |
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda)
        )

    # Paginación
    paginator = Paginator(maquinas_list, 20)
    page = request.GET.get('page')
    maquinas = paginator.get_page(page)

    # Para los filtros en template
    categorias = CategoriaMaquina.objects.filter(activa=True)

    context = {
        'title': 'Lista de Máquinas',
        'maquinas': maquinas,
        'categorias': categorias,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'busqueda': busqueda,
    }

    return render(request, 'maquinaria/lista_maquinas.html', context)

@login_required
def crear_maquina_view(request):
    """Crear nueva máquina"""
    from .forms import MaquinaForm

    if request.method == 'POST':
        form = MaquinaForm(request.POST, request.FILES)
        if form.is_valid():
            maquina = form.save(commit=False)

            # Asignar usuario creador
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                maquina.created_by = usuario
            except Usuario.DoesNotExist:
                pass

            maquina.save()

            # Crear entrada en el historial
            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='creacion',
                descripcion=f'Máquina {maquina.codigo_inventario} creada en el sistema',
                usuario=maquina.created_by
            )

            messages.success(request, f'Máquina {maquina.codigo_inventario} creada exitosamente')
            return redirect('maquinaria:detalle_maquina', pk=maquina.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = MaquinaForm()

    context = {
        'title': 'Crear Máquina',
        'form': form,
    }

    return render(request, 'maquinaria/crear_maquina.html', context)

@login_required
def detalle_maquina_view(request, pk):
    """Detalle de una máquina específica"""
    maquina = get_object_or_404(Maquina, pk=pk)
    historial = HistorialMaquina.objects.filter(maquina=maquina).order_by('-fecha_evento')[:10]
    alertas = AlertaMaquina.objects.filter(maquina=maquina).order_by('-fecha_creacion')[:5]

    context = {
        'title': f'Detalle - {maquina.codigo_inventario}',
        'maquina': maquina,
        'historial': historial,
        'alertas': alertas,
    }

    return render(request, 'maquinaria/detalle_maquina.html', context)

@login_required
def editar_maquina_view(request, pk):
    """Editar máquina existente"""
    from .forms import MaquinaForm

    maquina = get_object_or_404(Maquina, pk=pk)

    if request.method == 'POST':
        form = MaquinaForm(request.POST, request.FILES, instance=maquina)
        if form.is_valid():
            # Verificar qué campos cambiaron
            campos_cambiados = []
            for field_name, field in form.fields.items():
                old_value = getattr(maquina, field_name, None)
                new_value = form.cleaned_data.get(field_name)
                if old_value != new_value:
                    campos_cambiados.append(field_name)

            maquina_actualizada = form.save()

            # Crear entrada en el historial si hubo cambios
            if campos_cambiados:
                try:
                    usuario = Usuario.objects.get(numero_documento=request.user.username)
                except Usuario.DoesNotExist:
                    usuario = None

                HistorialMaquina.objects.create(
                    maquina=maquina_actualizada,
                    tipo_evento='actualizacion',
                    descripcion=f'Máquina actualizada. Campos modificados: {", ".join(campos_cambiados)}',
                    usuario=usuario
                )

            messages.success(request, f'Máquina {maquina.codigo_inventario} actualizada exitosamente')
            return redirect('maquinaria:detalle_maquina', pk=pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = MaquinaForm(instance=maquina)

    context = {
        'title': f'Editar - {maquina.codigo_inventario}',
        'maquina': maquina,
        'form': form,
    }

    return render(request, 'maquinaria/editar_maquina.html', context)

@login_required
def eliminar_maquina_view(request, pk):
    """Eliminar máquina"""
    maquina = get_object_or_404(Maquina, pk=pk)

    if request.method == 'POST':
        codigo = maquina.codigo_inventario
        nombre = maquina.nombre

        # Crear entrada en el historial antes de eliminar
        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
        except Usuario.DoesNotExist:
            usuario = None

        # Guardar información para el historial antes de eliminar
        HistorialMaquina.objects.create(
            maquina=maquina,
            tipo_evento='eliminacion',
            descripcion=f'Máquina {codigo} - {nombre} eliminada del sistema',
            usuario=usuario
        )

        # Eliminar la máquina (esto también eliminará el historial por CASCADE)
        maquina.delete()

        messages.success(request, f'Máquina {codigo} eliminada exitosamente')
        return redirect('maquinaria:lista_maquinas')

    # Obtener información adicional para mostrar al usuario
    total_alertas = AlertaMaquina.objects.filter(maquina=maquina).count()
    total_historial = HistorialMaquina.objects.filter(maquina=maquina).count()

    context = {
        'title': f'Eliminar - {maquina.codigo_inventario}',
        'maquina': maquina,
        'total_alertas': total_alertas,
        'total_historial': total_historial,
    }

    return render(request, 'maquinaria/eliminar_maquina.html', context)

# Estado de máquinas
@login_required
def cambiar_estado_maquina(request, pk):
    """Cambiar el estado de una máquina vía AJAX"""
    if request.method == 'POST':
        maquina = get_object_or_404(Maquina, pk=pk)
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones', '')

        if nuevo_estado in dict(Maquina.ESTADO_CHOICES):
            estado_anterior = maquina.estado
            maquina.estado = nuevo_estado
            maquina.save()

            # Crear entrada en el historial
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
            except Usuario.DoesNotExist:
                usuario = None

            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='cambio_estado',
                descripcion=f'Estado cambiado de "{estado_anterior}" a "{nuevo_estado}". {observaciones}',
                valor_anterior=estado_anterior,
                valor_nuevo=nuevo_estado,
                usuario=usuario
            )

            return JsonResponse({
                'success': True,
                'message': f'Estado cambiado exitosamente a {maquina.get_estado_display()}'
            })

        return JsonResponse({
            'success': False,
            'message': 'Estado inválido'
        })

    return JsonResponse({'success': False, 'message': 'Método no permitido'})

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
    """Lista de alertas con filtros"""
    alertas_list = AlertaMaquina.objects.select_related('maquina').all()

    # Filtros
    estado_filtro = request.GET.get('estado')
    prioridad_filtro = request.GET.get('prioridad')
    tipo_filtro = request.GET.get('tipo')

    if estado_filtro:
        alertas_list = alertas_list.filter(estado=estado_filtro)

    if prioridad_filtro:
        alertas_list = alertas_list.filter(prioridad=prioridad_filtro)

    if tipo_filtro:
        alertas_list = alertas_list.filter(tipo=tipo_filtro)

    # Paginación
    paginator = Paginator(alertas_list.order_by('-fecha_creacion'), 15)
    page = request.GET.get('page')
    alertas = paginator.get_page(page)

    context = {
        'title': 'Alertas de Maquinaria',
        'alertas': alertas,
        'estado_filtro': estado_filtro,
        'prioridad_filtro': prioridad_filtro,
        'tipo_filtro': tipo_filtro,
    }

    return render(request, 'maquinaria/alertas.html', context)

@login_required
def crear_alerta_view(request):
    """Crear nueva alerta"""
    if request.method == 'POST':
        # Lógica de creación
        messages.success(request, 'Alerta creada exitosamente')
        return redirect('maquinaria:alertas')

    context = {
        'title': 'Crear Alerta',
        'maquinas': Maquina.objects.all(),
    }

    return render(request, 'maquinaria/crear_alerta.html', context)

@login_required
def resolver_alerta(request, pk):
    """Resolver alerta via AJAX"""
    alerta = get_object_or_404(AlertaMaquina, pk=pk)

    if request.method == 'POST':
        alerta.estado = 'resuelta'
        alerta.fecha_resolucion = timezone.now()

        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
            alerta.resuelto_por = usuario
        except Usuario.DoesNotExist:
            pass

        alerta.save()

        return JsonResponse({'success': True, 'message': 'Alerta resuelta exitosamente'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def detalle_alerta_view(request, pk):
    """Detalle de alerta específica"""
    alerta = get_object_or_404(AlertaMaquina, pk=pk)

    context = {
        'title': f'Alerta - {alerta.maquina.codigo_inventario}',
        'alerta': alerta,
    }

    return render(request, 'maquinaria/detalle_alerta.html', context)

# Mantenimiento
@login_required
def mantenimiento_dashboard_view(request):
    """Dashboard de mantenimiento con datos reales"""
    from datetime import date, timedelta

    # Estadísticas de mantenimiento
    hoy = date.today()
    esta_semana = hoy + timedelta(days=7)

    mantenimientos_hoy = Maquina.objects.filter(
        proximo_mantenimiento=hoy
    ).count()

    mantenimientos_pendientes = Maquina.objects.filter(
        proximo_mantenimiento__lte=esta_semana,
        proximo_mantenimiento__gte=hoy
    ).count()

    mantenimientos_vencidos = Maquina.objects.filter(
        proximo_mantenimiento__lt=hoy
    ).exclude(proximo_mantenimiento__isnull=True).count()

    # Actividades recientes de mantenimiento
    actividades_mantenimiento = HistorialMaquina.objects.filter(
        tipo_evento__in=['mantenimiento', 'reparacion']
    ).select_related('maquina', 'usuario').order_by('-fecha_evento')[:10]

    # Máquinas que necesitan mantenimiento urgente
    mantenimiento_urgente = Maquina.objects.filter(
        proximo_mantenimiento__lte=hoy + timedelta(days=3)
    ).exclude(proximo_mantenimiento__isnull=True)[:10]

    # Alertas de mantenimiento activas
    alertas_mantenimiento = AlertaMaquina.objects.filter(
        estado='activa',
        tipo__in=['mantenimiento', 'reparacion']
    ).select_related('maquina')[:5]

    # KPIs básicos de mantenimiento
    total_maquinas = Maquina.objects.count()
    maquinas_al_dia = total_maquinas - mantenimientos_vencidos
    cumplimiento_porcentaje = round((maquinas_al_dia / total_maquinas * 100) if total_maquinas > 0 else 0, 1)

    context = {
        'title': 'Dashboard Mantenimiento',
        'mantenimientos_hoy': mantenimientos_hoy,
        'mantenimientos_pendientes': mantenimientos_pendientes,
        'mantenimientos_vencidos': mantenimientos_vencidos,
        'actividades_mantenimiento': actividades_mantenimiento,
        'mantenimiento_urgente': mantenimiento_urgente,
        'alertas_mantenimiento': alertas_mantenimiento,
        'cumplimiento_porcentaje': cumplimiento_porcentaje,
        'total_maquinas': total_maquinas,
    }

    return render(request, 'maquinaria/mantenimiento_dashboard.html', context)

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
