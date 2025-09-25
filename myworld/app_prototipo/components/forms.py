from django import forms
from .models import Configuracion, Notificacion, Widget, MenuPersonalizado

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['clave', 'valor', 'tipo_valor', 'descripcion', 'categoria', 'publico', 'modificable']
        widgets = {
            'clave': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'clave_configuracion'
            }),
            'valor': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Valor de la configuración'
            }),
            'tipo_valor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción de la configuración...'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: general, email, sistema'
            }),
            'publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'modificable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        exclude = ['fecha_creacion', 'fecha_envio', 'fecha_lectura', 'fecha_archivado', 'enviado_por_sistema']
        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la notificación'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mensaje de la notificación...'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: bi-bell, bi-info-circle'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'requiere_accion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'url_accion': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la acción (opcional)'
            }),
            'texto_accion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto del botón de acción'
            }),
            'maquina_relacionada': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alerta_relacionada': forms.Select(attrs={
                'class': 'form-select'
            }),
            'metadatos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Metadatos en formato JSON (opcional)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from usuarios.models import Usuario
        from maquinaria.models import Maquina, AlertaMaquina

        self.fields['usuario'].queryset = Usuario.objects.filter(estado='activo')
        self.fields['maquina_relacionada'].queryset = Maquina.objects.exclude(estado='retirada')
        self.fields['maquina_relacionada'].empty_label = "Sin máquina relacionada"
        self.fields['alerta_relacionada'].queryset = AlertaMaquina.objects.filter(estado='activa')
        self.fields['alerta_relacionada'].empty_label = "Sin alerta relacionada"

class WidgetForm(forms.ModelForm):
    class Meta:
        model = Widget
        exclude = ['fecha_creacion', 'fecha_actualizacion', 'datos_cache', 'cache_actualizado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del widget'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del widget...'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'configuracion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Configuración en formato JSON'
            }),
            'css_personalizado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'CSS personalizado (opcional)'
            }),
            'javascript_personalizado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'JavaScript personalizado (opcional)'
            }),
            'fuente_datos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Método o endpoint para obtener datos'
            }),
            'query_personalizada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Query SQL o filtros personalizados'
            }),
            'parametros_datos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Parámetros en formato JSON'
            }),
            'cache_duracion_segundos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '30',
                'max': '3600'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'requiere_permisos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Lista de permisos en formato JSON'
            }),
            'creado_por': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from usuarios.models import Usuario
        self.fields['creado_por'].queryset = Usuario.objects.filter(estado='activo')

class MenuPersonalizadoForm(forms.ModelForm):
    class Meta:
        model = MenuPersonalizado
        fields = ['nombre', 'icono', 'url', 'orden', 'abrir_nueva_ventana', 'color', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del menú'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: bi-star, bi-bookmark'
            }),
            'url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '/ruta/del/enlace/'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'abrir_nueva_ventana': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción del enlace...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class BusquedaAvanzadaForm(forms.Form):
    """Formulario para búsqueda avanzada en el sistema"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Buscar en todo el sistema...',
            'autocomplete': 'off'
        })
    )

    modulos = forms.MultipleChoiceField(
        choices=[
            ('maquinaria', 'Maquinaria'),
            ('usuarios', 'Usuarios'),
            ('documentos', 'Documentos'),
            ('reportes', 'Reportes'),
            ('ia_assistant', 'Asistente IA'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=['maquinaria', 'documentos']
    )

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class BusquedaInteligentForm(forms.Form):
    """Formulario para búsqueda inteligente con IA"""
    query = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe lo que buscas en lenguaje natural...'
        })
    )

    contexto = forms.ChoiceField(
        choices=[
            ('general', 'Búsqueda general'),
            ('problemas', 'Problemas y soluciones'),
            ('mantenimiento', 'Mantenimiento'),
            ('documentacion', 'Documentación'),
        ],
        initial='general',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class ConfiguracionSistemaForm(forms.Form):
    """Formulario para configuraciones generales del sistema"""

    # Configuraciones generales
    nombre_sistema = forms.CharField(
        initial='Sistema SENA - Gestión Maquinaria',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    logo_sistema = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    tema_principal = forms.ChoiceField(
        choices=[
            ('sena-azul', 'Azul SENA'),
            ('sena-verde', 'Verde SENA'),
            ('oscuro', 'Tema Oscuro'),
            ('personalizado', 'Personalizado')
        ],
        initial='sena-azul',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    # Configuraciones de seguridad
    max_intentos_login = forms.IntegerField(
        initial=5,
        min_value=3,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

    duracion_sesion_minutos = forms.IntegerField(
        initial=480,  # 8 horas
        min_value=60,
        max_value=1440,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

    # Configuraciones de notificaciones
    activar_notificaciones_email = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    servidor_smtp = forms.CharField(
        initial='smtp.gmail.com',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    puerto_smtp = forms.IntegerField(
        initial=587,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

    email_remitente = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'sistema@sena.edu.co'
        })
    )

    # Configuraciones de mantenimiento
    backup_automatico = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    frecuencia_backup_horas = forms.IntegerField(
        initial=24,
        min_value=1,
        max_value=168,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

    limpiar_logs_dias = forms.IntegerField(
        initial=30,
        min_value=7,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

class LogsFilterForm(forms.Form):
    """Formulario para filtrar logs del sistema"""

    fecha_inicio = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    fecha_fin = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    nivel = forms.ChoiceField(
        choices=[('', 'Todos los niveles')] + [
            ('debug', 'Debug'),
            ('info', 'Información'),
            ('warning', 'Advertencia'),
            ('error', 'Error'),
            ('critical', 'Crítico')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    modulo = forms.ChoiceField(
        choices=[('', 'Todos los módulos')] + [
            ('usuarios', 'Usuarios'),
            ('maquinaria', 'Maquinaria'),
            ('reportes', 'Reportes'),
            ('ia_assistant', 'Asistente IA'),
            ('documentos', 'Documentos'),
            ('sistema', 'Sistema'),
            ('api', 'API'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    usuario = forms.ModelChoiceField(
        queryset=None,  # Se establece en __init__
        required=False,
        empty_label="Todos los usuarios",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    accion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filtrar por acción...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from usuarios.models import Usuario
        self.fields['usuario'].queryset = Usuario.objects.filter(estado='activo').order_by('nombres')

class ExportarLogsForm(forms.Form):
    """Formulario para exportar logs del sistema"""

    formato = forms.ChoiceField(
        choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel'),
            ('json', 'JSON'),
            ('txt', 'Texto plano')
        ],
        initial='csv',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    incluir_metadatos = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Incluir metadatos adicionales en la exportación'
    )

    agrupar_por_usuario = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Agrupar logs por usuario'
    )

class ContactoSoporteForm(forms.Form):
    """Formulario de contacto con soporte técnico"""

    asunto = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto del mensaje'
        })
    )

    categoria = forms.ChoiceField(
        choices=[
            ('bug', 'Reportar Error'),
            ('feature', 'Solicitar Función'),
            ('help', 'Solicitar Ayuda'),
            ('feedback', 'Dar Feedback'),
            ('other', 'Otro')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    prioridad = forms.ChoiceField(
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
            ('critica', 'Crítica')
        ],
        initial='media',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Describe detalladamente tu consulta...'
        })
    )

    adjuntos = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'multiple': True
        }),
        help_text='Archivos de soporte (capturas, logs, etc.)'
    )

    incluir_info_sistema = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Incluir información del sistema para mejor soporte'
    )