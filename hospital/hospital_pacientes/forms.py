from django import forms
from .models import Paciente,MenorACargoDePaciente
from controlUsuario.models import Persona
from hospital_personal.models import SolicitudReactivacion
from django.core.validators import RegexValidator  # Para permitir símbolos comunes en el campo de teléfono.

solo_letras_validator = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ]{2,}$',
    message='Este campo debe tener al menos 2 letras y solo contener letras.',
    code='invalid_letters'
)

PARENTESCO_CHOICES = [
    ('HIJO', 'Hijo/a'),
    ('NIETO', 'Nieto/a'),
    ('SOBRINO', 'Sobrino/a'),
    ('ABUELO', 'Abuelo/a'),
    ('HERMANO', 'Hermano/a mayor'),
    ('TUTOR_LEGAL', 'Tutor Legal'),
] 
class RegistrarMenorForm(forms.ModelForm):
    dni = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d+$',  # Permite solo números
                message="El DNI solo puede contener números.",
                code='invalid_dni'
            )
        ],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',  # Solo permite números 
            "placeholder" : "DNI",
            'class': "campos-modal"
        })
    )  
    parentesco = forms.ChoiceField(
        choices=PARENTESCO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'campos-modal',
            'required': '',
        }),
        label="Parentesco con el menor"
    )    
    first_name = forms.CharField(
        max_length=30,
        validators=[solo_letras_validator],
        widget=forms.TextInput(attrs={
            'class': "campos-modal",
            'required': "",
            'placeholder': "Ej. Roberto"
        })
    )
    last_name = forms.CharField(
        max_length=30,
        validators=[solo_letras_validator],
        widget=forms.TextInput(attrs={
            'class': "campos-modal",
            'required': "",
            'placeholder': "Ej. López"
        })
    )
    
    class Meta:
        model = Persona  # Este formulario esta basado sobre el modelo "Persona"
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'dni','first_name', 'last_name','sexo','fecha_nacimiento'
        ]
        widgets = {
            "sexo" : forms.Select(attrs={'class': "campos-modal", 'required':""}),
            "fecha_nacimiento" : forms.DateInput(attrs={'class': "campos-modal",'placeholder': 'DD/MM/YYYY','type': 'date', 'required':""}) ,
        }

    def __init__(self, *args, **kwargs):
        self.adulto = kwargs.pop('adulto', None)  # capturamos al adulto desde la vista
        self.instance = kwargs.get('instance', None)  # Obtenemos la instancia si estamos editando
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_nac = cleaned_data.get('fecha_nacimiento')
        
        if fecha_nac:
            from datetime import date
            edad = (date.today() - fecha_nac).days // 365
            if edad >= 18:
                raise forms.ValidationError("Este formulario es solo para registrar menores de edad.")
        
        return cleaned_data
    
    def save(self, commit=True):
        persona = super().save(commit=False)  # Guardamos primero la persona

        if commit:
            persona.save()

            # Asegúrate de que estás creando un objeto Paciente
            paciente, pacienteCreado = Paciente.objects.get_or_create(persona=persona)  # Usamos get_or_create para evitar duplicados

            try:
                if pacienteCreado:
                    paciente.save()  # Si el paciente es nuevo

                parentesco = self.cleaned_data.get('parentesco')

                # Verifica si ya existe un registro con este menor y adulto
                registro_existente = MenorACargoDePaciente.objects.filter(adulto=self.adulto, menor=paciente).first()

                if registro_existente:
                    # Si ya existe, actualiza los campos del registro
                    registro_existente.parentesco = parentesco
                    registro_existente.save()  # Guarda los cambios
                else:
                    # Si no existe, crea el registro
                    if self.adulto:
                        MenorACargoDePaciente.objects.create(
                            adulto=self.adulto,
                            menor=paciente,
                            parentesco=parentesco
                        )

            except Exception as e:
                print(f"Error al guardar paciente o crear registro del menor: {e}")

        return persona


solo_letras_validator = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ]{2,}$',
    message='Este campo debe tener al menos 2 letras y solo contener letras.',
    code='invalid_letters'
)
# Creamos un form para los campos del modelo/tabla Persona :
class FormularioRegistroPersonalizado(forms.ModelForm): 
    telefono = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d+$',  # Permite solo números
                message="El teléfono solo puede contener números.",
                code='invalid_telefono'
            )
        ],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',  # Solo permite números 
            "placeholder" : "Ej. 25489032",
            'required':""
        })
    )  
    dni = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d+$',  # Permite solo números
                message="El DNI solo puede contener números.",
                code='invalid_dni'
            )
        ],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',  # Solo permite números 
            "placeholder" : "DNI",
        })
    )  
    
    first_name = forms.CharField(
        max_length=30,
        validators=[solo_letras_validator],
        widget=forms.TextInput(attrs={
            'required': "",
            'placeholder': "Ej. Roberto"
        })
    )
    
    
    last_name = forms.CharField(
        max_length=30,
        validators=[solo_letras_validator],
        widget=forms.TextInput(attrs={
            'required': "",
            'placeholder': "Ej. López"
        })
    )
    
    login_id = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Ej. jose@gmail.com"
        })
    )

    
class SolicitudReactivacionForm(forms.ModelForm):
    dni = forms.CharField(
        required=True,
        label="DNI",
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d+$',  # Permite solo números
                message="El DNI solo puede contener números.",
                code='invalid_dni'
            )
        ],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',  # Solo permite números 
            "placeholder" : "DNI",
        })
    )      
    first_name = forms.CharField(
        required=True,
        label="Nombre",
        max_length=30,
        validators=[solo_letras_validator],
        widget=forms.TextInput(attrs={
            'required': "",
            'placeholder': "Ej. Roberto"
        })
    )    
    last_name = forms.CharField(
        required=True,
        label="Apellido",
        max_length=30,
        validators=[solo_letras_validator],
        widget=forms.TextInput(attrs={
            'required': "",
            'placeholder': "Ej. López"
        })
    )    
    fecha_nacimiento = forms.DateField(required=True, label="Fecha de nacimiento", widget=forms.DateInput(attrs={'type': 'date'}))

    login_id = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Opcional: Ej. jose@gmail.com"
        }),
        required=False,
        label="Email"
        
    )
    telefono = forms.CharField(
        required=False,
        label="Teléfono",
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d+$',  # Permite solo números
                message="El teléfono solo puede contener números.",
                code='invalid_telefono'
            )
        ],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',  # Solo permite números 
            "placeholder" : "Opcional: Ej. 25489032",
        })
    )      
    numero_paciente = forms.CharField(required=False, label="Número de paciente",widget=forms.TextInput(attrs={"placeholder":"Opcional"}))
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Agregue información adicional para ayudar al operador (Opcional)'}),
        label="Observaciones"
    )

    class Meta:
        model = SolicitudReactivacion
        fields = ['observaciones']  
        






