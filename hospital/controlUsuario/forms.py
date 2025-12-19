from django.contrib.auth.forms import AuthenticationForm
from django import forms  # Esta clase nos permite crear un Formulario en base de una Tabla/modelo
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator  # Para permitir símbolos comunes en el campo de teléfono.
from django.contrib.auth import authenticate 
from .models import Persona,Usuario
from hospital_pacientes.models import Paciente
from hospital_personal.models import UsuarioLugarTrabajoAsignado,UsuarioRolProfesionalAsignado
from controlUsuario.models import TiposUsuarios

class FormularioLoginPersonalizado(AuthenticationForm):   # Personalizamos el AuthenticationForm para poder agregarle clases a los inputs
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autofocus': 'autofocus','placeholder': 'Ingrese su email o legajo'}))  # <-- usar "username" aquí aunque sea login_id internamente
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}),label="Contraseña")

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = Persona.objects.get(login_id=username)  
            except Persona.DoesNotExist:
                raise ValidationError("Usuario y/o contraseña incorrectos.")
            
            # Verificamos si la cuenta está activa
            if not user.is_active:
                if hasattr(user, 'usuario'):
                    raise ValidationError("Esta cuenta está inactiva. Contacte al administrador.")
                if hasattr(user, 'paciente'):
                    raise ValidationError("Se detectó una cuenta previamente registrada con esta información. Debe reactivarla para continuar.")

            user = authenticate(self.request, username=username, password=password)

            if user is None:
                raise ValidationError("Usuario y/o contraseña incorrectos.")
    
            
            # asignacion = user.usuario.get_asignacionActual()
            # if asignacion["asignacion"] is None:
            #     raise ValidationError("No se ha registrado ninguna asignación para tu usuario. Por favor, contacta con administración para resolverlo.")
            
            # if not asignacion["dentro_del_turno"]:
            #     raise ValidationError("No puede iniciar sesión fuera de su horario laboral.")

            # Si todo está bien, guardamos el usuario en el cache
            self.user_cache = user

        return self.cleaned_data


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
    direccion = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'required': "",
            'placeholder': "Ej. Calle Falsa 123"
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

    
    class Meta:
        model = Persona  # Este formulario esta basado sobre el modelo "Persona"
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'login_id', 'password', 'dni','first_name', 'last_name','sexo',
            'telefono', 'fecha_nacimiento'
        ]
        widgets = {
            "sexo" : forms.Select(attrs={'required':""}),
            'password': forms.PasswordInput(attrs={'placeholder':"Contraseña"}),
            "fecha_nacimiento" : forms.DateInput(attrs={'type': 'date'},format='%Y-%m-%d')
        }
        
        
    def __init__(self, *args, **kwargs):
        super(FormularioRegistroPersonalizado, self).__init__(*args, **kwargs)

        # Hacer password no requerido si es edición
        if self.instance and self.instance.pk:
            self.fields['password'].required = False

            # Solo cargar dirección si el usuario ya existe
            try:
                paciente = Paciente.objects.get(persona=self.instance)
                self.fields['direccion'].initial = paciente.direccion
            except Paciente.DoesNotExist:
                pass
        
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return None
        
        if password and len(password) < 8:
            self.add_error('password', "La contraseña debe tener al menos 8 caracteres.")   
            
        return password  
    
    
    def clean_login_id(self):
        login_id = self.cleaned_data.get('login_id')
        persona = Persona.objects.filter(login_id=login_id)

        # Si estamos editando una instancia, la excluimos del filtro
        if self.instance.pk:
            persona = persona.exclude(pk=self.instance.pk)

        if persona.exists():
            raise ValidationError("Ya existe un usuario registrado con este identificador. Por favor, elige otro.")
        return login_id
    
    def save(self, commit=True):
        persona = super(FormularioRegistroPersonalizado, self).save(commit=False)

        if commit:
            persona.email = self.cleaned_data['login_id']
            
            nueva_contraseña = self.cleaned_data.get('password')  
            if nueva_contraseña:
                persona.set_password(nueva_contraseña) # Si se ingresó una nueva contraseña, la seteo correctamente
            else:
                # No modificar la contraseña: mantener la actual
                persona.password = persona.__class__.objects.get(pk=persona.pk).password # busco la contraseña actual en la base de datos (.objects.get()), y la vuelvo a asignar, sin tocarla. Para que no haya un re-hasheo de la contraseña. Sino hago esto se setearea como None debido a la funcion clean_password(self).
                
            persona.save()

            # Guardar o actualizar paciente
            try:
                paciente = Paciente.objects.get(persona=persona)
                paciente.direccion = self.cleaned_data['direccion']
            except Paciente.DoesNotExist:
                paciente = Paciente(persona=persona, direccion=self.cleaned_data['direccion'])

            try:
                paciente.save()
            except Exception as e:
                print(f"Error al guardar paciente: {e}")

        return persona
    
    # Validaciones : 
    # def clean_fecha_nacimiento(self):
    #     nacimiento = self.cleaned_data.get('fecha_nacimiento')
    #     if not nacimiento:
    #         raise ValidationError("Este campo es obligatorio.")
        
    #     hoy = date.today()
    #     edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
    #     if edad < 18:
    #         raise ValidationError("Debes tener al menos 18 años para registrarte.")
    #     return nacimiento

    # def clean_password(self):
    #     password = self.cleaned_data.get('password')

    #     if not re.match(r'^(?=.*[A-Za-zñÑ])(?=.*[A-ZñÑ])(?=.*\d)[A-Za-zñÑ\d._@#$%&*!?-]{6,}$', password):
    #         raise ValidationError("La contraseña debe tener al menos 6 caracteres, una letra mayúscula, un número, y puede incluir símbolos como . _ @ # $ % & * ! ? -")
    #     return password
    
    # def clean_username(self):
    #     username = self.cleaned_data['username']
        
    #     # if re.search(r'[^a-zA-ZñÑ0-9._-]', username): # Verificar que solo tenga letras,numeros,puntos,guion bajo y medio
    #     #     raise ValidationError("El nombre de usuario solo puede contener letras, números, puntos, guiones y guiones bajos.")

    #     # if not re.search(r'[a-zA-ZñÑ]', username):  # Verificar que tenga al menos una letra    
    #     #     raise ValidationError("Tu nombre de usuario debe contener por lo menos una letra.")

    #     if Persona.objects.filter(username=username).exists(): 
    #         raise ValidationError("Este nombre de usuario ya está en uso.")

    #     return username


class FormularioPersona(forms.ModelForm):
    telefono = forms.CharField(
        max_length=12,
        validators=[RegexValidator(
            regex=r'^\d+$',  # Permite solo números
            message="El teléfono solo puede contener números.",
            code='invalid_telefono'
        )],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',  # Solo permite números
            "placeholder": "Ej. 25489032",
            'required': ""
        })
    )
    first_name = forms.CharField(
        max_length=30,
        validators=[solo_letras_validator],  # Asumiendo que ya tienes este validador
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
    

    class Meta:
        model = Persona
        fields = ['login_id', 'password', 'dni', 'first_name', 'last_name', 'sexo', 'telefono', 'fecha_nacimiento', 'email',"is_active"]
        widgets = {
            "login_id": forms.TextInput(attrs={'autofocus': "", 'placeholder': "Ej. 1000"}),
            "dni": forms.TextInput(attrs={'autofocus': "", 'placeholder': "DNI", 'required': ""}),
            "email": forms.EmailInput(attrs={'required': "", 'placeholder': "Ej. roberto45@gmail.com"}),
            "sexo": forms.Select(attrs={'required': ""}),
            'password': forms.PasswordInput(attrs={'placeholder': "Contraseña"}),
            "fecha_nacimiento": forms.DateInput(attrs={'type': 'date', 'required': ""},format='%Y-%m-%d'),
            "is_active": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        persona_instance = kwargs.pop('persona_instance', None)
        super().__init__(*args, **kwargs)
        self.fields["login_id"].required = True
        # Si estamos editando (es decir, hay una persona_instance), no queremos que la contraseña sea obligatoria
        if persona_instance:
            self.fields['login_id'].widget.attrs['readonly'] = True
            self.fields['password'].required = False  

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return None
        return password
    
    def clean_login_id(self):
        login_id = self.cleaned_data.get('login_id')
        
        if self.instance.pk and login_id != self.instance.login_id:  # Si estamos editando, no permitir cambiar login_id
            raise ValidationError("No está permitido modificar el Número de Legajo.")
        
        if not login_id.isdigit():  # Validar que solo sean numeros
            raise ValidationError("El N° Legajo solo puede contener números.")
        
        # Si estamos editando una instancia, la excluimos del filtro
        persona = Persona.objects.filter(login_id=login_id)
        if self.instance.pk:
            persona = persona.exclude(pk=self.instance.pk)

        if persona.exists():
            raise ValidationError("Ya existe un usuario registrado con este identificador. Por favor, elige otro.")
        
        return login_id
    
    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active')
        
        if self.instance.pk and is_active == False: 
            usuario = Usuario.objects.get(persona=self.instance.pk)
            if UsuarioRolProfesionalAsignado.objects.filter(usuario=usuario).exists():                
                raise ValidationError("No es posible deshabilitar este usuario porque posee asignaciones de rol profesional activas.Retire dichas asignaciones antes de intentar deshabilitarlo.")
            
            if UsuarioLugarTrabajoAsignado.objects.filter(usuario=usuario).exists():                
                raise ValidationError("No es posible deshabilitar este usuario porque posee asignaciones de lugar de trabajo activas.Retire dichas asignaciones antes de intentar deshabilitarlo.")

class FormularioUsuario(forms.ModelForm):
    numero_matricula = forms.CharField(
        max_length=30,
        required=False,
        validators=[RegexValidator(
            regex=r'^\d+$',  # Permite solo números
            message="La matricula solo puede contener números.",
            code='invalid_matricula'
        )],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',  # Solo permite números
            "placeholder": "Ingrese el N° de matricula"
        })
    )

    class Meta:
        model = Usuario
        fields = ['numero_matricula', 'tipoUsuario']
        widgets = {
            "tipoUsuario": forms.Select(attrs={'required': "", "id":"id_tipoUsuarioForm"}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user",None)
        super().__init__(*args, **kwargs)   
        if self.user and self.user.usuario.tipoUsuario.id == 2:
            tipoUsuario = TiposUsuarios.objects.exclude(pk__in=[1,2])
            self.fields["tipoUsuario"].queryset = tipoUsuario
    
    def clean(self):
        cleaned_data = super().clean()
        numero_matricula = cleaned_data.get('numero_matricula')
        tipoUsuario = cleaned_data.get('tipoUsuario')
        
        if self.instance.pk:
            if self.instance.tipoUsuario != tipoUsuario:
                if self.instance.rolesProfesionalesUsuario.exists():
                    self.add_error('tipoUsuario', 'Debes eliminar los "Roles profesionales" del usuario para poder cambiar el tipo de usuario.')
                    return cleaned_data
                elif self.instance.UsuariosAsignadosAEsteLugar.exists():
                    self.add_error('tipoUsuario', 'Debes eliminar los "Lugares donde presta servicios" el usuario para poder cambiar el tipo de usuario.')
                    return cleaned_data
                    

        # Lista de usuarios que requieren matrícula:
        tipoUsuarios_que_requieren_matricula = [3, 4, 5, 7, 8]  #medico,enfermero,apoyo en diagnostico y tratamiento,jefe de enfermeria, medico tratante

        if tipoUsuario and tipoUsuario.id in tipoUsuarios_que_requieren_matricula: # Si el tipo de usuario requiere matricula
            if not numero_matricula:
                self.add_error('numero_matricula', 'Este tipo de usuario requiere ingresar un número de matrícula.')

        # Si hay número de matrícula, validamos que sea único
        if numero_matricula:
            # Verificamos unicidad manualmente (porque el modelo no puede usar unique=True con null/blank)
            qs = Usuario.objects.filter(numero_matricula=numero_matricula)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('numero_matricula', 'Este número de matrícula ya está en uso.')

        return cleaned_data


# Formulario combinado (para manejar ambos modelos a la vez)
class FormularioRegistroDePersonal(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user",None)
        persona_instance = kwargs.pop('persona_instance', None)
        usuario_instance = kwargs.pop('usuario_instance', None)
        super().__init__(*args, **kwargs)
        

        self.persona_form = FormularioPersona(
            *args,
            instance=persona_instance,  # Si se pasa una instancia de persona seria una edicion , mientras que si se pasa un None seria una alta 
            persona_instance=persona_instance  
        )

        self.usuario_form = FormularioUsuario(
            *args, 
            instance=usuario_instance,  # Si se pasa una instancia de usuario seria una edicion , mientras que si se pasa un None seria una alta 
            user = self.user

        )
            
    def is_valid(self): # Le estás diciendo a Django: "Este formulario combinado solo es válido si ambos formularios internos lo son."
        return self.persona_form.is_valid() and self.usuario_form.is_valid()
    
    def save(self, commit=True):
        persona = self.persona_form.save(commit=False)
        usuario = self.usuario_form.save(commit=False)
        # Si se ingresó una nueva contraseña, seteala correctamente
        password = self.persona_form.cleaned_data.get('password')
        if password:
            # Solo seteamos una nueva contraseña si fue ingresada (en texto plano)
            persona.set_password(password)
        else:
            # No modificar la contraseña: mantener la actual
            persona.password = persona.__class__.objects.get(pk=persona.pk).password # busco la contraseña actual en la base de datos (.objects.get()), y la vuelvo a asignar, sin tocarla. Para que no haya un re-hasheo de la contraseña. Sino hago esto se setearea como None debido a la funcion clean_password(self).

        if commit:
            persona.save()
            usuario.persona = persona
            usuario.save()
            
        return usuario


class FormularioActualizarPassword(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'}),
        label='Contraseña'
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'}),
        label='Confirmar Contraseña'
    )

    class Meta:
        model = Persona
        fields = ['password'] 

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password and confirmar_password and password != confirmar_password:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")

        if password and len(password) < 8:
            self.add_error('password', "La contraseña debe tener al menos 8 caracteres.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance


class FormularioNuevaPassword(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'}),
        label='Contraseña'
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'}),
        label='Confirmar Contraseña'
    )
    login_id = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Ej. jose@gmail.com"
        })
    )    

    class Meta:
        model = Persona
        fields = ["login_id",'password'] 

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password and confirmar_password and password != confirmar_password:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")

        if password and len(password) < 8:
            self.add_error('password', "La contraseña debe tener al menos 8 caracteres.")

        return cleaned_data
    
    def clean_login_id(self):
        login_id = self.cleaned_data.get('login_id')
        persona = Persona.objects.filter(login_id=login_id)

        # Si estamos editando una instancia, la excluimos del filtro
        if self.instance.pk:
            persona = persona.exclude(pk=self.instance.pk)

        if persona.exists():
            raise ValidationError("Ya existe un usuario registrado con este identificador. Por favor, elige otro.")
        return login_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data['password'])
        instance.email = self.cleaned_data['login_id']
        instance.is_active = True
        if commit:
            instance.save()
        return instance
    



