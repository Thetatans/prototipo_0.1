from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Usuario, TipoUsuario, SesionUsuario
from .forms import (
    LoginForm, UsuarioForm, RegistroUsuarioForm, PerfilUsuarioForm,
    CambiarPasswordForm, BuscarUsuariosForm
)

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Intentar autenticar por número de documento o email
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Registrar sesión
                try:
                    usuario = Usuario.objects.get(numero_documento=username)
                    SesionUsuario.objects.create(
                        usuario=usuario,
                        token_sesion=request.session.session_key or '',
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    # Actualizar último acceso
                    usuario.ultimo_acceso = timezone.now()
                    usuario.save()
                except Usuario.DoesNotExist:
                    pass

                messages.success(request, f'¡Bienvenido!')
                return redirect('usuarios:dashboard')
            else:
                messages.error(request, 'Credenciales inválidas')

    return render(request, 'usuarios/modern_login.html', {
        'form': form,
        'title': 'Iniciar Sesión - SENA'
    })

@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
        usuario.sesiones.filter(activa=True).update(
            fecha_fin=timezone.now(),
            activa=False
        )
    except Usuario.DoesNotExist:
        pass

    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('usuarios:login')

@login_required
def dashboard_view(request):
    """Dashboard principal después del login"""
    # Estadísticas básicas
    total_maquinas = 0
    maquinas_operativas = 0
    alertas_activas = 0

    try:
        from maquinaria.models import Maquina, AlertaMaquina
        total_maquinas = Maquina.objects.count()
        maquinas_operativas = Maquina.objects.filter(estado='operativa').count()
        alertas_activas = AlertaMaquina.objects.filter(estado='activa').count()
    except ImportError:
        pass

    # Notificaciones recientes
    notificaciones_recientes = []
    try:
        from components.models import Notificacion
        usuario = Usuario.objects.get(numero_documento=request.user.username)
        notificaciones_recientes = Notificacion.objects.filter(
            usuario=usuario,
            estado__in=['pendiente', 'enviada']
        ).order_by('-fecha_creacion')[:5]
    except (ImportError, Usuario.DoesNotExist):
        pass

    context = {
        'title': 'Dashboard - SENA',
        'total_maquinas': total_maquinas,
        'maquinas_operativas': maquinas_operativas,
        'alertas_activas': alertas_activas,
        'notificaciones_recientes': notificaciones_recientes,
    }

    return render(request, 'usuarios/dashboard.html', context)

@login_required
def perfil_view(request):
    """Vista del perfil de usuario"""
    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
    except Usuario.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado')
        return redirect('usuarios:dashboard')

    form = PerfilUsuarioForm(instance=usuario)
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('usuarios:perfil')

    return render(request, 'usuarios/perfil.html', {
        'form': form,
        'usuario': usuario,
        'title': 'Mi Perfil - SENA'
    })

@login_required
def lista_usuarios_view(request):
    """Vista para listar usuarios (solo admin)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    form = BuscarUsuariosForm(request.GET or None)
    usuarios = Usuario.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        tipo_usuario = form.cleaned_data.get('tipo_usuario')
        estado = form.cleaned_data.get('estado')
        centro_formacion = form.cleaned_data.get('centro_formacion')

        if query:
            usuarios = usuarios.filter(
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(numero_documento__icontains=query) |
                Q(email__icontains=query)
            )
        if tipo_usuario:
            usuarios = usuarios.filter(tipo_usuario=tipo_usuario)
        if estado:
            usuarios = usuarios.filter(estado=estado)
        if centro_formacion:
            usuarios = usuarios.filter(centro_formacion__icontains=centro_formacion)

    paginator = Paginator(usuarios.order_by('-fecha_registro'), 20)
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)

    return render(request, 'usuarios/lista_usuarios.html', {
        'form': form,
        'usuarios': usuarios,
        'title': 'Gestión de Usuarios - SENA'
    })

@login_required
def crear_usuario_view(request):
    """Vista para crear usuario (solo admin)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    form = UsuarioForm()
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            try:
                usuario.created_by = Usuario.objects.get(numero_documento=request.user.username)
            except Usuario.DoesNotExist:
                pass
            usuario.save()
            messages.success(request, f'Usuario {usuario.nombre_completo} creado correctamente')
            return redirect('usuarios:lista')

    return render(request, 'usuarios/crear_usuario.html', {
        'form': form,
        'title': 'Crear Usuario - SENA'
    })

@login_required
def editar_usuario_view(request, pk):
    """Vista para editar usuario (solo admin)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(instance=usuario)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.nombre_completo} actualizado correctamente')
            return redirect('usuarios:lista')

    return render(request, 'usuarios/editar_usuario.html', {
        'form': form,
        'usuario': usuario,
        'title': f'Editar {usuario.nombre_completo} - SENA'
    })

@login_required
def detalle_usuario_view(request, pk):
    """Vista de detalle de usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)

    # Solo admin o el mismo usuario puede ver detalles
    if not request.user.is_staff and request.user.username != usuario.numero_documento:
        messages.error(request, 'No tienes permisos para ver esta información')
        return redirect('usuarios:dashboard')

    # Estadísticas adicionales
    sesiones_recientes = SesionUsuario.objects.filter(
        usuario=usuario
    ).order_by('-fecha_inicio')[:10]

    return render(request, 'usuarios/detalle_usuario.html', {
        'usuario': usuario,
        'sesiones_recientes': sesiones_recientes,
        'title': f'{usuario.nombre_completo} - SENA'
    })

@login_required
@require_http_methods(["POST"])
def cambiar_estado_usuario(request, pk):
    """Vista para cambiar estado de usuario (solo admin)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    usuario = get_object_or_404(Usuario, pk=pk)
    nuevo_estado = request.POST.get('estado')

    if nuevo_estado in dict(Usuario.ESTADO_CHOICES):
        usuario.estado = nuevo_estado
        if nuevo_estado == 'activo':
            usuario.fecha_aprobacion = timezone.now()
        usuario.save()

        return JsonResponse({'success': True, 'estado': usuario.get_estado_display()})

    return JsonResponse({'error': 'Estado no válido'}, status=400)

@login_required
def configuracion_view(request):
    """Vista de configuración general de usuarios"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    # Estadísticas
    stats = {
        'total_usuarios': Usuario.objects.count(),
        'usuarios_activos': Usuario.objects.filter(estado='activo').count(),
        'usuarios_pendientes': Usuario.objects.filter(estado='pendiente').count(),
        'sesiones_activas': SesionUsuario.objects.filter(activa=True).count(),
    }

    return render(request, 'usuarios/configuracion.html', {
        'stats': stats,
        'title': 'Configuración Usuarios - SENA'
    })

@login_required
def cambiar_password_view(request):
    """Vista para cambiar contraseña"""
    form = CambiarPasswordForm(user=request.user)
    if request.method == 'POST':
        form = CambiarPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            nueva_password = form.cleaned_data.get('password_nueva')
            request.user.set_password(nueva_password)
            request.user.save()
            messages.success(request, 'Contraseña cambiada correctamente')
            return redirect('usuarios:perfil')

    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
        'title': 'Cambiar Contraseña - SENA'
    })

def register_view(request):
    """Vista de registro de usuarios"""
    form = RegistroUsuarioForm()
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.estado = 'pendiente'
            usuario.save()

            messages.success(request,
                'Registro exitoso. Tu cuenta está pendiente de aprobación por un administrador.')
            return redirect('usuarios:login')

    return render(request, 'usuarios/register.html', {
        'form': form,
        'title': 'Registro - SENA'
    })

# API Views para AJAX
@login_required
def buscar_usuarios_api(request):
    """API para buscar usuarios via AJAX"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    usuarios = Usuario.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(numero_documento__icontains=query) |
        Q(email__icontains=query)
    )[:10]

    results = []
    for usuario in usuarios:
        results.append({
            'id': usuario.id,
            'text': f"{usuario.nombre_completo} ({usuario.numero_documento})",
            'email': usuario.email,
            'estado': usuario.estado
        })

    return JsonResponse({'results': results})

@login_required
def estadisticas_usuarios_api(request):
    """API para estadísticas de usuarios"""
    stats = {
        'total': Usuario.objects.count(),
        'por_estado': dict(Usuario.objects.values_list('estado').annotate(count=Count('estado'))),
        'por_tipo': list(Usuario.objects.values('tipo_usuario__nombre').annotate(count=Count('tipo_usuario'))),
        'registros_mes': Usuario.objects.filter(
            fecha_registro__month=timezone.now().month
        ).count()
    }

    return JsonResponse(stats)
