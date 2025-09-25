from django.db import models
import uuid

class Configuracion(models.Model):
    TIPO_VALOR_CHOICES = [
        ('string', 'Texto'),
        ('integer', 'Número Entero'),
        ('float', 'Número Decimal'),
        ('boolean', 'Verdadero/Falso'),
        ('json', 'JSON'),
        ('date', 'Fecha'),
        ('datetime', 'Fecha y Hora'),
        ('email', 'Correo Electrónico'),
        ('url', 'URL'),
    ]

    clave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    tipo_valor = models.CharField(max_length=10, choices=TIPO_VALOR_CHOICES, default='string')
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=50, default='general')

    # Control de acceso
    publico = models.BooleanField(default=False)
    modificable = models.BooleanField(default=True)

    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"
        ordering = ['categoria', 'clave']

    def __str__(self):
        return f"{self.clave} = {self.valor[:50]}"

    def get_valor_typed(self):
        if self.tipo_valor == 'integer':
            return int(self.valor)
        elif self.tipo_valor == 'float':
            return float(self.valor)
        elif self.tipo_valor == 'boolean':
            return self.valor.lower() in ('true', '1', 'yes', 'on')
        elif self.tipo_valor == 'json':
            import json
            return json.loads(self.valor)
        return self.valor

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('system', 'Sistema'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('leida', 'Leída'),
        ('archivada', 'Archivada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )

    # Contenido
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    icono = models.CharField(max_length=50, default='bi-bell')

    # Estado y fechas
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    fecha_archivado = models.DateTimeField(null=True, blank=True)

    # Configuración
    requiere_accion = models.BooleanField(default=False)
    url_accion = models.URLField(blank=True)
    texto_accion = models.CharField(max_length=100, blank=True)

    # Relaciones opcionales
    maquina_relacionada = models.ForeignKey(
        'maquinaria.Maquina',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    alerta_relacionada = models.ForeignKey(
        'maquinaria.AlertaMaquina',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    # Metadatos
    metadatos = models.JSONField(default=dict, blank=True)
    enviado_por_sistema = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre_completo}"

class LogActividad(models.Model):
    NIVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Crítico'),
    ]

    MODULO_CHOICES = [
        ('usuarios', 'Usuarios'),
        ('maquinaria', 'Maquinaria'),
        ('reportes', 'Reportes'),
        ('ia_assistant', 'Asistente IA'),
        ('documentos', 'Documentos'),
        ('sistema', 'Sistema'),
        ('api', 'API'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información básica
    timestamp = models.DateTimeField(auto_now_add=True)
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='info')
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='sistema')

    # Usuario y sesión
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    sesion_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Acción realizada
    accion = models.CharField(max_length=100)
    descripcion = models.TextField()
    objeto_tipo = models.CharField(max_length=50, blank=True)  # Modelo afectado
    objeto_id = models.CharField(max_length=100, blank=True)  # ID del objeto

    # Detalles técnicos
    request_method = models.CharField(max_length=10, blank=True)  # GET, POST, etc.
    request_path = models.CharField(max_length=500, blank=True)
    user_agent = models.TextField(blank=True)

    # Metadatos adicionales
    datos_adicionales = models.JSONField(default=dict, blank=True)
    tiempo_ejecucion = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = "Log de Actividad"
        verbose_name_plural = "Logs de Actividad"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['modulo', 'timestamp']),
            models.Index(fields=['nivel']),
            models.Index(fields=['accion']),
        ]

    def __str__(self):
        usuario_str = self.usuario.nombre_completo if self.usuario else 'Sistema'
        return f"{self.timestamp} - {usuario_str} - {self.accion}"

class Widget(models.Model):
    TIPO_WIDGET_CHOICES = [
        ('contador', 'Contador'),
        ('grafico_linea', 'Gráfico de Líneas'),
        ('grafico_barra', 'Gráfico de Barras'),
        ('grafico_pastel', 'Gráfico de Pastel'),
        ('tabla', 'Tabla'),
        ('mapa', 'Mapa'),
        ('calendario', 'Calendario'),
        ('lista', 'Lista'),
        ('estado', 'Indicador de Estado'),
        ('progreso', 'Barra de Progreso'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_WIDGET_CHOICES)

    # Configuración visual
    configuracion = models.JSONField(default=dict)
    css_personalizado = models.TextField(blank=True)
    javascript_personalizado = models.TextField(blank=True)

    # Datos
    fuente_datos = models.CharField(max_length=200, blank=True)  # Método o API endpoint
    query_personalizada = models.TextField(blank=True)  # SQL o filtros específicos
    parametros_datos = models.JSONField(default=dict, blank=True)

    # Cache
    cache_duracion_segundos = models.IntegerField(default=300)  # 5 minutos
    datos_cache = models.JSONField(default=dict, blank=True)
    cache_actualizado = models.DateTimeField(null=True, blank=True)

    # Control
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    requiere_permisos = models.JSONField(default=list, blank=True)

    # Metadatos
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='widgets_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Widget"
        verbose_name_plural = "Widgets"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

class MenuPersonalizado(models.Model):
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='menus_personalizados'
    )

    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=50, default='bi-star')
    url = models.CharField(max_length=200)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    # Configuración adicional
    abrir_nueva_ventana = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#007bff')
    descripcion = models.TextField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Menú Personalizado"
        verbose_name_plural = "Menús Personalizados"
        ordering = ['usuario', 'orden', 'nombre']
        unique_together = ['usuario', 'nombre']

    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.nombre}"
