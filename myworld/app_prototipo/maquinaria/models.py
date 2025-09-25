from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid

class CategoriaMaquina(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, default='bi-gear')
    color = models.CharField(max_length=7, default='#007bff', help_text="Color en formato hexadecimal")
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de Máquina"
        verbose_name_plural = "Categorías de Máquinas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, unique=True)
    contacto_nombre = models.CharField(max_length=100)
    contacto_telefono = models.CharField(max_length=20)
    contacto_email = models.EmailField()
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='Colombia')
    sitio_web = models.URLField(blank=True)
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Maquina(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('operativa', 'Operativa'),
        ('mantenimiento', 'En Mantenimiento'),
        ('reparacion', 'En Reparación'),
        ('fuera_servicio', 'Fuera de Servicio'),
        ('retirada', 'Retirada'),
    ]

    CONDICION_CHOICES = [
        ('excelente', 'Excelente'),
        ('buena', 'Buena'),
        ('regular', 'Regular'),
        ('mala', 'Mala'),
        ('critica', 'Crítica'),
    ]

    # Información básica
    codigo_inventario = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaMaquina, on_delete=models.PROTECT)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)

    # Estado y condición
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    condicion = models.CharField(max_length=20, choices=CONDICION_CHOICES, default='excelente')

    # Especificaciones técnicas
    especificaciones_tecnicas = models.TextField(blank=True)
    capacidad = models.CharField(max_length=200, blank=True)
    potencia = models.CharField(max_length=100, blank=True)
    voltaje = models.CharField(max_length=50, blank=True)
    dimensiones = models.CharField(max_length=100, blank=True)
    peso = models.CharField(max_length=50, blank=True)

    # Ubicación
    ubicacion = models.CharField(max_length=200)
    centro_formacion = models.CharField(max_length=200)
    ambiente_formacion = models.CharField(max_length=200, blank=True)
    responsable = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='maquinas_asignadas'
    )

    # Información de compra
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_adquisicion = models.DateField()
    valor_adquisicion = models.DecimalField(max_digits=15, decimal_places=2)
    numero_factura = models.CharField(max_length=100, blank=True)
    garantia_meses = models.IntegerField(default=12)

    # Datos de uso
    horas_uso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_uso_mes = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    eficiencia = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100, help_text="Porcentaje de eficiencia"
    )

    # Mantenimiento
    fecha_ultimo_mantenimiento = models.DateField(null=True, blank=True)
    proximo_mantenimiento = models.DateField(null=True, blank=True)
    frecuencia_mantenimiento_dias = models.IntegerField(default=90)

    # Archivos y documentos
    imagen = models.ImageField(upload_to='maquinaria/imagenes/', blank=True, null=True)
    manual_pdf = models.FileField(upload_to='maquinaria/manuales/', blank=True, null=True)
    ficha_tecnica = models.FileField(upload_to='maquinaria/fichas/', blank=True, null=True)

    # Metadatos
    observaciones = models.TextField(blank=True)
    qr_code = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='maquinas_creadas'
    )

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"
        ordering = ['codigo_inventario']
        indexes = [
            models.Index(fields=['codigo_inventario']),
            models.Index(fields=['estado']),
            models.Index(fields=['categoria']),
            models.Index(fields=['centro_formacion']),
        ]

    def __str__(self):
        return f"{self.codigo_inventario} - {self.nombre}"

    def get_absolute_url(self):
        return reverse('maquinaria:detalle', kwargs={'pk': self.pk})

    @property
    def necesita_mantenimiento(self):
        if not self.proximo_mantenimiento:
            return False
        from django.utils import timezone
        return self.proximo_mantenimiento <= timezone.now().date()

    @property
    def tiempo_sin_mantenimiento(self):
        if not self.fecha_ultimo_mantenimiento:
            return None
        from django.utils import timezone
        return (timezone.now().date() - self.fecha_ultimo_mantenimiento).days

class AlertaMaquina(models.Model):
    TIPO_CHOICES = [
        ('mantenimiento', 'Mantenimiento Programado'),
        ('reparacion', 'Reparación Urgente'),
        ('eficiencia', 'Baja Eficiencia'),
        ('uso_excesivo', 'Uso Excesivo'),
        ('garantia', 'Garantía por Vencer'),
        ('inspeccion', 'Inspección Requerida'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('en_proceso', 'En Proceso'),
        ('resuelta', 'Resuelta'),
        ('ignorada', 'Ignorada'),
    ]

    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='alertas')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelto_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertas_resueltas'
    )

    notas_resolucion = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertas_creadas'
    )

    class Meta:
        verbose_name = "Alerta de Máquina"
        verbose_name_plural = "Alertas de Máquinas"
        ordering = ['-fecha_creacion', '-prioridad']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['prioridad']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        return f"{self.maquina.codigo_inventario} - {self.titulo}"

class HistorialMaquina(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('creacion', 'Creación'),
        ('mantenimiento', 'Mantenimiento'),
        ('reparacion', 'Reparación'),
        ('cambio_estado', 'Cambio de Estado'),
        ('cambio_ubicacion', 'Cambio de Ubicación'),
        ('cambio_responsable', 'Cambio de Responsable'),
        ('actualizacion', 'Actualización de Datos'),
        ('inspeccion', 'Inspección'),
    ]

    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='historial')
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    descripcion = models.TextField()
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    costo_asociado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    fecha_evento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    archivos_adjuntos = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Historial de Máquina"
        verbose_name_plural = "Historiales de Máquinas"
        ordering = ['-fecha_evento']
        indexes = [
            models.Index(fields=['maquina', '-fecha_evento']),
            models.Index(fields=['tipo_evento']),
        ]

    def __str__(self):
        return f"{self.maquina.codigo_inventario} - {self.get_tipo_evento_display()} ({self.fecha_evento})"
