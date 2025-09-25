from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class ConsultaIA(models.Model):
    TIPO_CONSULTA_CHOICES = [
        ('diagnostico', 'Diagnóstico de Problema'),
        ('mantenimiento', 'Recomendación de Mantenimiento'),
        ('optimizacion', 'Optimización de Procesos'),
        ('prediccion', 'Predicción de Fallas'),
        ('general', 'Consulta General'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completada', 'Completada'),
        ('error', 'Error'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='consultas_ia'
    )
    maquina = models.ForeignKey(
        'maquinaria.Maquina',
        on_delete=models.CASCADE,
        related_name='consultas_ia',
        null=True, blank=True
    )

    # Consulta
    tipo_consulta = models.CharField(max_length=20, choices=TIPO_CONSULTA_CHOICES, default='general')
    titulo = models.CharField(max_length=200)
    consulta_texto = models.TextField()
    contexto_adicional = models.JSONField(default=dict, blank=True)

    # Respuesta
    respuesta_ia = models.TextField(blank=True)
    confianza_respuesta = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True,
        help_text="Nivel de confianza de la IA (0-100%)"
    )
    recomendaciones = models.JSONField(default=list, blank=True)

    # Estado y metadatos
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    tiempo_procesamiento = models.DurationField(null=True, blank=True)

    # Feedback del usuario
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Calificación de 1 a 5 estrellas"
    )
    feedback_texto = models.TextField(blank=True)
    util = models.BooleanField(null=True, blank=True)

    # Fechas
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_feedback = models.DateTimeField(null=True, blank=True)

    # Archivos adjuntos
    archivos_consulta = models.JSONField(default=list, blank=True)
    imagenes_diagnostico = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Consulta IA"
        verbose_name_plural = "Consultas IA"
        ordering = ['-fecha_consulta']
        indexes = [
            models.Index(fields=['usuario', '-fecha_consulta']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_consulta']),
            models.Index(fields=['maquina']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre_completo}"

class ConocimientoIA(models.Model):
    CATEGORIA_CHOICES = [
        ('maquinaria', 'Maquinaria y Equipos'),
        ('mantenimiento', 'Mantenimiento'),
        ('seguridad', 'Seguridad Industrial'),
        ('procesos', 'Procesos de Manufactura'),
        ('diagnostico', 'Diagnóstico de Fallas'),
        ('normatividad', 'Normatividad y Estándares'),
    ]

    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    palabras_clave = models.JSONField(default=list)

    # Metadatos para la IA
    vectores_embedding = models.JSONField(default=list, blank=True)
    relevancia_score = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=1.0,
        help_text="Score de relevancia para el sistema de IA"
    )

    # Uso y estadísticas
    veces_utilizado = models.IntegerField(default=0)
    ultima_utilizacion = models.DateTimeField(null=True, blank=True)
    efectividad_promedio = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Efectividad promedio según feedback de usuarios"
    )

    # Control de versiones
    version = models.CharField(max_length=10, default='1.0')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Conocimiento IA"
        verbose_name_plural = "Base de Conocimiento IA"
        ordering = ['-relevancia_score', '-fecha_actualizacion']
        indexes = [
            models.Index(fields=['categoria']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.get_categoria_display()})"

class PrediccionIA(models.Model):
    TIPO_PREDICCION_CHOICES = [
        ('falla_inminente', 'Falla Inminente'),
        ('mantenimiento_preventivo', 'Mantenimiento Preventivo'),
        ('optimizacion_uso', 'Optimización de Uso'),
        ('vida_util', 'Estimación Vida Útil'),
        ('costo_mantenimiento', 'Predicción de Costos'),
    ]

    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('cumplida', 'Cumplida'),
        ('descartada', 'Descartada'),
        ('en_seguimiento', 'En Seguimiento'),
    ]

    maquina = models.ForeignKey(
        'maquinaria.Maquina',
        on_delete=models.CASCADE,
        related_name='predicciones_ia'
    )
    tipo_prediccion = models.CharField(max_length=30, choices=TIPO_PREDICCION_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()

    # Predicción
    fecha_prediccion = models.DateTimeField(auto_now_add=True)
    fecha_estimada_evento = models.DateTimeField()
    probabilidad = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Probabilidad del evento (0-100%)"
    )
    confianza = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Nivel de confianza de la predicción (0-100%)"
    )

    # Datos utilizados para la predicción
    datos_entrada = models.JSONField(default=dict)
    modelo_ia_utilizado = models.CharField(max_length=100, blank=True)
    version_modelo = models.CharField(max_length=20, blank=True)

    # Seguimiento
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    fecha_cumplimiento = models.DateTimeField(null=True, blank=True)
    precision_real = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Precisión real después de validar la predicción"
    )

    # Acciones recomendadas
    acciones_recomendadas = models.JSONField(default=list, blank=True)
    costo_estimado_accion = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    ahorro_estimado = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Predicción IA"
        verbose_name_plural = "Predicciones IA"
        ordering = ['-fecha_prediccion', '-probabilidad']
        indexes = [
            models.Index(fields=['maquina', '-fecha_prediccion']),
            models.Index(fields=['tipo_prediccion']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_estimada_evento']),
        ]

    def __str__(self):
        return f"{self.maquina.codigo_inventario} - {self.titulo}"

class SesionChatIA(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='sesiones_chat_ia'
    )
    titulo = models.CharField(max_length=200, blank=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actividad = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True)
    contexto = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Sesión Chat IA"
        verbose_name_plural = "Sesiones Chat IA"
        ordering = ['-fecha_ultima_actividad']

    def __str__(self):
        return f"Chat {self.usuario.nombre_completo} - {self.fecha_inicio}"

class MensajeChatIA(models.Model):
    TIPO_MENSAJE_CHOICES = [
        ('usuario', 'Usuario'),
        ('ia', 'Asistente IA'),
        ('sistema', 'Sistema'),
    ]

    sesion = models.ForeignKey(
        SesionChatIA,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_MENSAJE_CHOICES)
    contenido = models.TextField()
    metadatos = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Para mensajes de IA
    tiempo_procesamiento = models.DurationField(null=True, blank=True)
    tokens_utilizados = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Mensaje Chat IA"
        verbose_name_plural = "Mensajes Chat IA"
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.timestamp}"
