from django import forms
from .models import ConsultaIA, ConocimientoIA, PrediccionIA, SesionChatIA
from maquinaria.models import Maquina

class ConsultaIAForm(forms.ModelForm):
    class Meta:
        model = ConsultaIA
        fields = [
            'maquina', 'tipo_consulta', 'titulo', 'consulta_texto',
            'contexto_adicional', 'prioridad'
        ]
        widgets = {
            'maquina': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Seleccionar máquina (opcional)'
            }),
            'tipo_consulta': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título breve de la consulta'
            }),
            'consulta_texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe tu consulta detalladamente...'
            }),
            'contexto_adicional': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Información adicional relevante (JSON o texto libre)'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo máquinas activas/operativas
        self.fields['maquina'].queryset = Maquina.objects.exclude(estado='retirada')
        self.fields['maquina'].empty_label = "Sin máquina específica"

class ConsultaRapidaForm(forms.Form):
    """Formulario simplificado para consultas rápidas"""
    consulta = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '¿Qué necesitas saber?'
        }),
        max_length=1000
    )
    maquina = forms.ModelChoiceField(
        queryset=Maquina.objects.exclude(estado='retirada'),
        required=False,
        empty_label="Sin máquina específica",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class DiagnosticoMaquinaForm(forms.Form):
    """Formulario específico para diagnósticos de máquinas"""
    maquina = forms.ModelChoiceField(
        queryset=Maquina.objects.exclude(estado='retirada'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    problema_descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe el problema que presenta la máquina...'
        }),
        max_length=2000
    )
    sintomas = forms.MultipleChoiceField(
        choices=[
            ('ruido', 'Ruido extraño'),
            ('vibracion', 'Vibración excesiva'),
            ('temperatura', 'Temperatura alta'),
            ('humo', 'Humo o vapores'),
            ('fuga', 'Fugas de fluidos'),
            ('error_display', 'Error en pantalla'),
            ('no_enciende', 'No enciende'),
            ('funciona_lento', 'Funciona lento'),
            ('parada_inesperada', 'Paradas inesperadas'),
            ('calidad_trabajo', 'Problemas de calidad en trabajo'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False
    )
    imagenes = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'multiple': True
        }),
        required=False,
        help_text='Subir imágenes del problema (opcional)'
    )

class ConocimientoIAForm(forms.ModelForm):
    class Meta:
        model = ConocimientoIA
        fields = [
            'categoria', 'titulo', 'contenido', 'palabras_clave',
            'relevancia_score', 'version', 'activo'
        ]
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del conocimiento'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Contenido detallado del conocimiento...'
            }),
            'palabras_clave': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Palabras clave separadas por comas'
            }),
            'relevancia_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '1',
                'step': '0.0001'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1.0, 2.1'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_palabras_clave(self):
        palabras_clave = self.cleaned_data.get('palabras_clave', '')
        if palabras_clave:
            # Convertir string separado por comas a lista
            lista_palabras = [palabra.strip() for palabra in palabras_clave.split(',')]
            return lista_palabras
        return []

class BuscarConocimientoForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en base de conocimiento...'
        })
    )
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + ConocimientoIA.CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    activo_solamente = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class FeedbackConsultaForm(forms.Form):
    """Formulario para calificar y dar feedback sobre consultas IA"""
    calificacion = forms.ChoiceField(
        choices=[(i, f'{i} estrella{"s" if i != 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    util = forms.ChoiceField(
        choices=[
            (True, 'Sí, fue útil'),
            (False, 'No fue útil')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    feedback_texto = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Comentarios adicionales sobre la respuesta...'
        })
    )

class ChatMensajeForm(forms.Form):
    """Formulario para enviar mensajes en el chat IA"""
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Escribe tu mensaje...',
            'style': 'resize: none;'
        }),
        max_length=2000
    )

class PrediccionesConfigForm(forms.Form):
    """Formulario para configurar generación de predicciones"""
    maquinas_seleccionadas = forms.ModelMultipleChoiceField(
        queryset=Maquina.objects.exclude(estado='retirada'),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text='Dejar vacío para analizar todas las máquinas'
    )
    tipos_prediccion = forms.MultipleChoiceField(
        choices=PrediccionIA.TIPO_PREDICCION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        initial=['falla_inminente', 'mantenimiento_preventivo']
    )
    horizonte_dias = forms.IntegerField(
        initial=30,
        min_value=7,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Días hacia el futuro para generar predicciones'
    )

class FiltroConsultasForm(forms.Form):
    """Formulario para filtrar consultas del usuario"""
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    tipo_consulta = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + ConsultaIA.TIPO_CONSULTA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + ConsultaIA.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    maquina = forms.ModelChoiceField(
        queryset=Maquina.objects.exclude(estado='retirada'),
        required=False,
        empty_label="Todas las máquinas",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class ConfiguracionIAForm(forms.Form):
    """Formulario para configurar parámetros del sistema IA"""
    modelo_ia_activo = forms.CharField(
        initial='gpt-3.5-turbo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del modelo IA'
        }),
        help_text='Modelo de IA a utilizar para consultas'
    )
    temperatura_respuestas = forms.DecimalField(
        initial=0.7,
        min_value=0.0,
        max_value=1.0,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text='Creatividad de las respuestas (0.0 = conservador, 1.0 = creativo)'
    )
    max_tokens_respuesta = forms.IntegerField(
        initial=1000,
        min_value=100,
        max_value=4000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Máximo número de tokens por respuesta'
    )
    confianza_minima = forms.DecimalField(
        initial=70.0,
        min_value=0.0,
        max_value=100.0,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text='Confianza mínima para mostrar respuestas (%)'
    )
    activar_predicciones_automaticas = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Generar predicciones automáticamente'
    )
    frecuencia_predicciones_horas = forms.IntegerField(
        initial=24,
        min_value=1,
        max_value=168,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Frecuencia de generación de predicciones (horas)'
    )