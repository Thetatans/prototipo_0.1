from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Maquina, CategoriaMaquina, Proveedor, AlertaMaquina, HistorialMaquina, MantenimientoProgramado
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
    """Lista de alertas con filtros y estadísticas reales"""
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

    # Estadísticas reales de alertas
    from django.utils import timezone
    from datetime import date

    alertas_criticas = AlertaMaquina.objects.filter(
        estado='activa', prioridad='critica'
    ).count()

    alertas_altas = AlertaMaquina.objects.filter(
        estado='activa', prioridad='alta'
    ).count()

    alertas_medias = AlertaMaquina.objects.filter(
        estado='activa', prioridad='media'
    ).count()

    alertas_resueltas_hoy = AlertaMaquina.objects.filter(
        estado='resuelta',
        fecha_resolucion__date=date.today()
    ).count()

    # Estadísticas por tipo
    from django.db.models import Count
    tipos_alertas = AlertaMaquina.objects.filter(
        estado='activa'
    ).values('tipo').annotate(
        count=Count('id')
    ).order_by('-count')

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
        'alertas_criticas': alertas_criticas,
        'alertas_altas': alertas_altas,
        'alertas_medias': alertas_medias,
        'alertas_resueltas_hoy': alertas_resueltas_hoy,
        'tipos_alertas': tipos_alertas,
    }

    return render(request, 'maquinaria/alertas.html', context)

@login_required
def crear_alerta_view(request):
    """Crear nueva alerta con datos reales"""
    from .forms import AlertaMaquinaForm
    import json

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            maquina_id = request.POST.get('maquina')
            tipo_alerta = request.POST.get('tipo_alerta', 'mantenimiento')
            titulo = request.POST.get('titulo')
            prioridad = request.POST.get('prioridad', 'media')
            descripcion = request.POST.get('descripcion')
            categoria = request.POST.get('categoria')
            fecha_deteccion = request.POST.get('fecha_deteccion')
            detectado_por = request.POST.get('detectado_por', 'sistema')
            ubicacion_falla = request.POST.get('ubicacion_falla', '')
            impacto_operacional = request.POST.get('impacto_operacional', 'minimo')
            riesgo_seguridad = request.POST.get('riesgo_seguridad', 'nulo')
            tecnico_asignado = request.POST.get('tecnico_asignado')
            fecha_estimada = request.POST.get('fecha_estimada')

            # Obtener síntomas y acciones inmediatas
            sintomas = request.POST.getlist('sintomas')
            acciones_inmediatas = request.POST.getlist('acciones_inmediatas')

            # Validar datos requeridos
            if not all([maquina_id, titulo, descripcion]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('maquinaria:crear_alerta')

            # Obtener la máquina
            try:
                maquina = Maquina.objects.get(pk=maquina_id)
            except Maquina.DoesNotExist:
                messages.error(request, 'La máquina seleccionada no existe.')
                return redirect('maquinaria:crear_alerta')

            # Mapear tipo de alerta al modelo
            tipo_mapping = {
                'falla': 'reparacion',
                'mantenimiento': 'mantenimiento',
                'operacional': 'eficiencia'
            }
            tipo_modelo = tipo_mapping.get(tipo_alerta, 'mantenimiento')

            # Crear la alerta
            alerta = AlertaMaquina.objects.create(
                maquina=maquina,
                tipo=tipo_modelo,
                prioridad=prioridad,
                titulo=titulo,
                descripcion=descripcion,
                estado='activa'
            )

            # Obtener usuario creador
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                alerta.created_by = usuario
                alerta.save()
            except Usuario.DoesNotExist:
                pass

            # Crear entrada en el historial
            datos_adicionales = {
                'categoria': categoria,
                'detectado_por': detectado_por,
                'ubicacion_falla': ubicacion_falla,
                'sintomas': sintomas,
                'impacto_operacional': impacto_operacional,
                'riesgo_seguridad': riesgo_seguridad,
                'acciones_inmediatas': acciones_inmediatas,
                'tecnico_asignado': tecnico_asignado,
                'fecha_estimada': fecha_estimada
            }

            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='alerta_creada',
                descripcion=f'Alerta creada: {titulo} (Prioridad: {prioridad})',
                valor_nuevo=json.dumps(datos_adicionales, ensure_ascii=False),
                usuario=alerta.created_by
            )

            # Actualizar estado de máquina si es crítica
            if prioridad in ['critica', 'emergencia']:
                estado_anterior = maquina.estado
                if 'suspender_operacion' in acciones_inmediatas:
                    maquina.estado = 'fuera_servicio'
                    maquina.save()

                    # Crear entrada adicional en historial para cambio de estado
                    HistorialMaquina.objects.create(
                        maquina=maquina,
                        tipo_evento='cambio_estado',
                        descripcion=f'Estado cambiado automáticamente por alerta crítica: {titulo}',
                        valor_anterior=estado_anterior,
                        valor_nuevo=maquina.estado,
                        usuario=alerta.created_by
                    )

            messages.success(request, f'Alerta "{titulo}" creada exitosamente para {maquina.codigo_inventario}')
            return redirect('maquinaria:detalle_alerta', pk=alerta.pk)

        except Exception as e:
            messages.error(request, f'Error al crear la alerta: {str(e)}')
            return redirect('maquinaria:crear_alerta')

    # GET request - mostrar formulario
    try:
        # Intentar obtener usuarios con filtro, si falla usar todos los usuarios
        usuarios_tecnicos = Usuario.objects.all().order_by('first_name', 'last_name')[:20]  # Limitar a 20 para performance
    except Exception:
        usuarios_tecnicos = []

    context = {
        'title': 'Crear Alerta',
        'maquinas': Maquina.objects.select_related('categoria').all().order_by('codigo_inventario'),
        'usuarios_tecnicos': usuarios_tecnicos,
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

        # Crear entrada en el historial
        HistorialMaquina.objects.create(
            maquina=alerta.maquina,
            tipo_evento='alerta_resuelta',
            descripcion=f'Alerta resuelta: {alerta.titulo}',
            usuario=alerta.resuelto_por
        )

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

    # Estadísticas de mantenimiento programado
    hoy = timezone.now().date()
    esta_semana = hoy + timedelta(days=7)

    # Mantenimientos programados para hoy
    mantenimientos_hoy = MantenimientoProgramado.objects.filter(
        fecha_programada__date=hoy,
        estado='programado'
    ).count()

    # Mantenimientos pendientes esta semana
    mantenimientos_pendientes = MantenimientoProgramado.objects.filter(
        fecha_programada__date__lte=esta_semana,
        fecha_programada__date__gte=hoy,
        estado='programado'
    ).count()

    # Mantenimientos vencidos
    mantenimientos_vencidos = MantenimientoProgramado.objects.filter(
        fecha_programada__date__lt=hoy,
        estado='programado'
    ).count()

    # Actividades recientes de mantenimiento
    actividades_mantenimiento = HistorialMaquina.objects.filter(
        tipo_evento__in=['mantenimiento', 'reparacion']
    ).select_related('maquina', 'usuario').order_by('-fecha_evento')[:10]

    # Mantenimientos programados próximos (usando el nuevo modelo)
    mantenimientos_proximos = MantenimientoProgramado.objects.filter(
        fecha_programada__date__lte=hoy + timedelta(days=7),
        fecha_programada__date__gte=hoy,
        estado='programado'
    ).select_related('maquina', 'tecnico_asignado').order_by('fecha_programada')[:10]

    # Alertas de mantenimiento activas
    alertas_mantenimiento = AlertaMaquina.objects.filter(
        estado='activa',
        tipo__in=['mantenimiento', 'reparacion']
    ).select_related('maquina')[:5]

    # KPIs básicos de mantenimiento
    total_mantenimientos_programados = MantenimientoProgramado.objects.filter(
        estado__in=['programado', 'en_progreso']
    ).count()

    if total_mantenimientos_programados > 0:
        mantenimientos_al_dia = total_mantenimientos_programados - mantenimientos_vencidos
        cumplimiento_porcentaje = round((mantenimientos_al_dia / total_mantenimientos_programados * 100), 1)
    else:
        cumplimiento_porcentaje = 100.0

    # Técnicos disponibles/ocupados
    from django.db.models import Case, When, Value, CharField
    tecnicos_estado = Usuario.objects.annotate(
        estado_actual=Case(
            When(mantenimientos_asignados__estado='en_progreso', then=Value('ocupado')),
            default=Value('disponible'),
            output_field=CharField()
        )
    ).values('id', 'nombres', 'apellidos', 'cargo', 'estado_actual')[:10]

    context = {
        'title': 'Dashboard Mantenimiento',
        'mantenimientos_hoy': mantenimientos_hoy,
        'mantenimientos_pendientes': mantenimientos_pendientes,
        'mantenimientos_vencidos': mantenimientos_vencidos,
        'actividades_mantenimiento': actividades_mantenimiento,
        'mantenimientos_proximos': mantenimientos_proximos,
        'alertas_mantenimiento': alertas_mantenimiento,
        'cumplimiento_porcentaje': cumplimiento_porcentaje,
        'tecnicos_estado': tecnicos_estado,
    }

    return render(request, 'maquinaria/mantenimiento_dashboard.html', context)

@login_required
def programar_mantenimiento_view(request, pk=None):
    """Programar nuevo mantenimiento con datos reales"""
    import json
    from datetime import timedelta

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            maquina_id = request.POST.get('maquina')
            tipo = request.POST.get('tipo', 'preventivo')
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            prioridad = request.POST.get('prioridad', 'media')
            fecha_programada = request.POST.get('fecha_programada')
            duracion_estimada = request.POST.get('duracion_estimada', '02:00:00')  # Default 2 horas
            tecnico_asignado_id = request.POST.get('tecnico_asignado')

            # Obtener listas de componentes, herramientas y repuestos
            componentes = request.POST.getlist('componentes')
            herramientas = request.POST.getlist('herramientas')
            repuestos = request.POST.getlist('repuestos')
            procedimientos = request.POST.get('procedimientos', '')
            costo_estimado = request.POST.get('costo_estimado')

            # Validar datos requeridos
            if not all([maquina_id, titulo, descripcion, fecha_programada]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('maquinaria:programar_mantenimiento')

            # Obtener la máquina
            try:
                maquina = Maquina.objects.get(pk=maquina_id)
            except Maquina.DoesNotExist:
                messages.error(request, 'La máquina seleccionada no existe.')
                return redirect('maquinaria:programar_mantenimiento')

            # Obtener técnico si fue asignado
            tecnico_asignado = None
            if tecnico_asignado_id:
                try:
                    tecnico_asignado = Usuario.objects.get(pk=tecnico_asignado_id)
                except Usuario.DoesNotExist:
                    pass

            # Convertir duración estimada
            try:
                horas, minutos, segundos = duracion_estimada.split(':')
                duracion_td = timedelta(hours=int(horas), minutes=int(minutos), seconds=int(segundos))
            except:
                duracion_td = timedelta(hours=2)  # Default 2 horas

            # Crear el mantenimiento programado
            mantenimiento = MantenimientoProgramado.objects.create(
                maquina=maquina,
                tipo=tipo,
                titulo=titulo,
                descripcion=descripcion,
                prioridad=prioridad,
                fecha_programada=fecha_programada,
                duracion_estimada=duracion_td,
                tecnico_asignado=tecnico_asignado,
                componentes_revisar=componentes,
                herramientas_necesarias=herramientas,
                repuestos_necesarios=repuestos,
                procedimientos=procedimientos,
                costo_estimado=float(costo_estimado) if costo_estimado else None
            )

            # Obtener usuario creador
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                mantenimiento.created_by = usuario
                mantenimiento.save()
            except Usuario.DoesNotExist:
                pass

            # Crear entrada en el historial
            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='mantenimiento',
                descripcion=f'Mantenimiento programado: {titulo} para {fecha_programada}',
                usuario=mantenimiento.created_by
            )

            messages.success(request, f'Mantenimiento "{titulo}" programado exitosamente para {maquina.codigo_inventario}')
            return redirect('maquinaria:mantenimiento_dashboard')

        except Exception as e:
            messages.error(request, f'Error al programar el mantenimiento: {str(e)}')
            return redirect('maquinaria:programar_mantenimiento')

    # GET request - mostrar formulario
    maquina_seleccionada = None
    if pk:
        try:
            maquina_seleccionada = Maquina.objects.get(pk=pk)
        except Maquina.DoesNotExist:
            pass

    try:
        usuarios_tecnicos = Usuario.objects.all().order_by('nombres', 'apellidos')[:20]
    except Exception:
        usuarios_tecnicos = []

    context = {
        'title': 'Programar Mantenimiento',
        'maquinas': Maquina.objects.select_related('categoria').all().order_by('codigo_inventario'),
        'maquina_seleccionada': maquina_seleccionada,
        'usuarios_tecnicos': usuarios_tecnicos,
    }

    return render(request, 'maquinaria/programar_mantenimiento.html', context)

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
