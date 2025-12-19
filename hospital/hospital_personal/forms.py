from django import forms
from django.forms import modelformset_factory # permite trabajar con múltiples formularios del mismo tipo en una sola vista.
from .models import Especialidades,Departamento,Consultas, OrdenEstudio, Medicaciones,EstudiosDiagnosticos,ResultadoEstudio,ResultadoImagen,UsuarioLugarTrabajoAsignado,UsuarioRolProfesionalAsignado,Lugar,Jorna_laboral,ServicioDiagnostico,PlantillaEstudio,Turno,TurnoEstudio,AsignacionesHabitaciones,AsignacionEnfermero,AsignacionMedico,ObservacionesEnfermero,ObservacionesMedico,AltaMedica
from controlUsuario.models import TiposUsuarios,RolesProfesionales,Usuario
from hospital_pacientes.models import Paciente
from django.core.exceptions import ValidationError
import datetime
from dal import autocomplete
from django.db.models import Count


class FormEspecialidades(forms.ModelForm): 
    class Meta:
        model = Especialidades  # Este formulario esta basado sobre el modelo "Especialidades"
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'nombre_especialidad', 'descripcion','permite_turno',"capacidad_diaria",'departamento'
        ]
        widgets = {
            "nombre_especialidad" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el nombre de la especialidad"}),
            "descripcion" : forms.Textarea(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese una descripcion"}),
            "permite_turno" : forms.CheckboxInput(attrs={'class': "campos-modal"}),
            "capacidad_diaria" : forms.NumberInput(attrs={'class': "campos-modal", 'placeholder':"Indique el número máximo de personas que pueden asistir por día"}),
            "departamento" : forms.Select(attrs={'class': "campos-modal"})
        }

class FormDepartamentos(forms.ModelForm): 
    class Meta:
        model = Departamento  # Este formulario esta basado sobre el modelo "Departamento"
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'nombre_departamento', 'tipo', 'descripcion'
        ]
        widgets = {
            "nombre_departamento" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el nombre del departamento"}),
            "tipo" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el tipo"}),
            "descripcion" : forms.Textarea(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese una descripcion"}),
        }

class FormServiciosDiagnostico(forms.ModelForm): 
    class Meta:
        model = ServicioDiagnostico 
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'nombre_servicio', 'descripcion', 'departamento',"capacidad_diaria","lugar"
        ]
        widgets = {
            "nombre_servicio" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el nombre del servicio de diagnostico"}),
            "descripcion" : forms.Textarea(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese una descripcion"}),
            "departamento" : forms.Select(attrs={'class': "campos-modal"}),
            "capacidad_diaria" : forms.NumberInput(attrs={'class': "campos-modal", 'placeholder':"Indique el número máximo de personas que pueden asistir por día"}),
            "lugar" : forms.CheckboxSelectMultiple(attrs={'class': "box-multipleCheck"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lugar'].queryset = Lugar.objects.filter(tipo__in=["lab", "img","diag_func","unidad_atenc","proc"], activo=True)  # Laboratorios         
        self.fields['lugar'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.abreviacion}) - Departamento: {obj.departamento}"



class FormEstudiosDiagnosticos(forms.ModelForm): 
    class Meta:
        model = EstudiosDiagnosticos 
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'nombre_estudio', 'especialidad', 'servicio_diagnostico',"tipo_resultado"
        ]
        widgets = {
            "nombre_estudio" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el nombre del estudio"}),
            "especialidad" : forms.CheckboxSelectMultiple(attrs={'class': "box-multipleCheck"}),
            "servicio_diagnostico" : forms.Select(attrs={'class': "campos-modal"}),
            "tipo_resultado" : forms.Select(attrs={'class': "campos-modal"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizando los labels de los ForeignKey en el formulario
        self.fields['servicio_diagnostico'].queryset = ServicioDiagnostico.objects.all()
        self.fields['especialidad'].queryset = Especialidades.objects.all()
        
        # Cambiar el texto que aparece en el Select sin cambiar el __str__ del modelo
        self.fields['servicio_diagnostico'].label_from_instance = lambda obj: f"{obj.nombre_servicio}" 
        self.fields['especialidad'].label_from_instance = lambda obj: f"{obj.nombre_especialidad}" 

class FormLugar(forms.ModelForm): 
    class Meta:
        model = Lugar 
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'nombre', 'tipo', 'piso',"sala","abreviacion","capacidad","departamento","descripcion","es_critico","activo","unidad"
        ]
        widgets = {
            "nombre" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el nombre del lugar"}),
            "tipo" : forms.Select(attrs={'class': "campos-modal"}),
            "piso" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el piso en el que esta ubicado el lugar"}),
            "sala" : forms.NumberInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el N° de sala"}),
            "abreviacion" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese la abreviación del nombre del lugar"}),
            "capacidad" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese la capacidad del lugar"}),
            "unidad" : forms.Select(attrs={'class': "campos-modal"}),
            "departamento" : forms.Select(attrs={'class': "campos-modal"}),
            "descripcion" : forms.Textarea(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese una descripcion del lugar"}),
            "es_critico" : forms.CheckboxInput(attrs={'class': "campos-modal"}),
            "activo" : forms.CheckboxInput(attrs={'class': "campos-modal"})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tipo = self.data.get("tipo") or (self.instance and self.instance.tipo)
                
        if tipo == "unidad_atenc": # Si el tipo de lugar es "unidad de atencion" hacemos esos campos opcionales
            self.fields["sala"].required = False
            self.fields["capacidad"].required = False
            self.fields["activo"].required = False        
        
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")

        if tipo == "unidad_atenc":
            if cleaned_data.get("sala") not in [None, ""]:
                self.add_error("sala", "La unidad de atención no necesita un número de sala.")
            if cleaned_data.get("capacidad") not in [None, ""]:
                self.add_error("capacidad", "La unidad de atención no necesita completar este campo.")
            if cleaned_data.get("unidad") not in [None, ""]:
                self.add_error("unidad",'No puedes seleccionar ninguna opción de unidad si el tipo es "Unidad de atención".')

            cleaned_data["sala"] = None
            cleaned_data["capacidad"] = 200
            cleaned_data["activo"] = True
        else:
            if cleaned_data.get("sala") is None:
                self.add_error("sala", "Este campo es obligatorio.")
            if cleaned_data.get("capacidad") in [None, ""]:
                cleaned_data["capacidad"] = 1  # default
            if cleaned_data.get("activo") is None:
                cleaned_data["activo"] = True # defauklt

        return cleaned_data
                



class FormPlantillaEstudio(forms.ModelForm): 
    class Meta:
        model = PlantillaEstudio 
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            "estudio","estructura"
        ]
        widgets = {
            "estudio" : forms.Select(attrs={'class': "campos-modal"}),
            "estructura" : forms.Textarea(attrs={'class': "campos-modal",'placeholder':"Ingrese la estructura en formato JSON del estudio"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizando los labels de los ForeignKey en el formulario
        self.fields['estudio'].queryset = EstudiosDiagnosticos.objects.all()
        
        # Cambiar el texto que aparece en el Select sin cambiar el __str__ del modelo
        self.fields['estudio'].label_from_instance = lambda obj: f"{obj.nombre_estudio}" 


class FormTiposUsuarios(forms.ModelForm): 
    class Meta:
        model = TiposUsuarios  
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'nombre_tipoUsuario'
        ]
        widgets = {
            "nombre_tipoUsuario" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el nuevo tipo de usuario"})
        }

class FormRolesProfesionales(forms.ModelForm): 
    class Meta:
        model = RolesProfesionales  
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            'nombre_rol_profesional',"tipoUsuario","especialidad","servicio_diagnostico","departamento"
        ]
        widgets = {
            "nombre_rol_profesional" : forms.TextInput(attrs={'class': "campos-modal",'autofocus':"", 'placeholder':"Ingrese el nombre del rol"}),
            "tipoUsuario" : forms.Select(attrs={'class': "campos-modal"}),
            "especialidad" : forms.Select(attrs={'class': "campos-modal"}),
            "servicio_diagnostico" : forms.Select(attrs={'class': "campos-modal"}),
            "departamento" : forms.Select(attrs={'class': "campos-modal"})
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'especialidad' in self.fields:
            self.fields['especialidad'].queryset = Especialidades.objects.all()
            self.fields['especialidad'].label_from_instance = lambda obj: f"{obj.nombre_especialidad}"

        if 'servicio_diagnostico' in self.fields:
            self.fields['servicio_diagnostico'].queryset = ServicioDiagnostico.objects.all()
            self.fields['servicio_diagnostico'].label_from_instance = lambda obj: f"{obj.nombre_servicio}"

        if 'departamento' in self.fields:
            self.fields['departamento'].queryset = Departamento.objects.all()
            self.fields['departamento'].label_from_instance = lambda obj: f"{obj.nombre_departamento}"
            
    def clean(self):
        cleaned_data = super().clean()
        tipoUsuario = cleaned_data.get("tipoUsuario")
        especialidad = cleaned_data.get("especialidad")
        departamento = cleaned_data.get("departamento")
        servicio_diagnostico = cleaned_data.get("servicio_diagnostico")
        
        if not tipoUsuario:
            return cleaned_data  
        
                
        if tipoUsuario.id in [3,4,8]: # Medico de consultorio, enfermero y medico hospitalario
            if especialidad is None or servicio_diagnostico or departamento:
                self.add_error(None, f"Un {tipoUsuario.nombre_tipoUsuario} debe estar asignado a una especialidad exclusivamente.")
        elif tipoUsuario.id == 7: # Jefe de enfermeria
            if departamento is None or especialidad or servicio_diagnostico:
                self.add_error(None, f"Un {tipoUsuario.nombre_tipoUsuario} debe estar asignado a un departamento exclusivamente.")
        elif tipoUsuario.id == 5: # Apoyo en Diagnóstico y Tratamiento
            if servicio_diagnostico is None or especialidad or departamento:
                self.add_error(None, f'Un usuario de "{tipoUsuario.nombre_tipoUsuario}" debe estar asignado a un servicio de diagnóstico exclusivamente.')
        else:
            if especialidad or servicio_diagnostico or departamento:
                self.add_error(None, f"Un {tipoUsuario.nombre_tipoUsuario} no puede estar asignado a una especialidad, a un servicio de diagnóstico o un departamento.")        
        
        return cleaned_data



class FormularioLugarTrabajo(forms.Form): # Cambiar el formulario base de ModelForm a Form Porque ModelForm espera que cada campo del modelo tenga correspondencia exacta en el formulario y en este caso eso no se cumple ya que vamos a manejar "jornada" como si fuera una relacion ManyToMany pese a que sea FK.
    rolProfesionalAsignado = forms.ModelChoiceField(
        queryset=UsuarioRolProfesionalAsignado.objects.all(),
        widget=forms.Select(attrs={"class": "campos-modal"}),
        label="Rol profesional"
    )
    lugar = forms.ModelChoiceField(
        queryset=Lugar.objects.all(),
        widget=forms.Select(attrs={"class": "campos-modal"}),
        label="Lugar"
    )
    jornada = forms.ModelMultipleChoiceField( # Seleccionar varias jornadas
        queryset=Jorna_laboral.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "box-multipleCheck"}), # Seleccionar varias jornadas
        label="Jornadas"
    )
    id_usuario = forms.CharField(widget=forms.HiddenInput(attrs={"id":"identificadorUsuario"}), required=False)    


    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)  # Pasar usuario desde la vista
        super().__init__(*args, **kwargs)
        
        if not self.usuario:
            raise ValueError("Se requiere un usuario para inicializar el formulario.")
        
        tipo_usuario = self.usuario.tipoUsuario.id
        
        if tipo_usuario == 1:  # Superadmin
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)              
        elif tipo_usuario == 2:  # Admin
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)              
        elif tipo_usuario == 3: # Medicos de consulta
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo__in=["cons","proc"],activo=True) #Los médicos trabajan en consultorios y pueden realizar procedimientos ambulatorios no quirúrgicos
        elif tipo_usuario == 4: # Enfermeros
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo__in=["hab","unidad_atenc"],activo=True)  # Los enfermeros se desempeñan principalmente en internación y unidades de atención
        elif tipo_usuario == 5: # Apoyo en Diagnóstico y Tratamiento (Radiologos,ecografista,tecnico en laboratorio , etc  )
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo__in=["lab", "img","diag_func","proc"], activo=True)  # Laboratorios 
        elif tipo_usuario == 6: # Cargador de resultados
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)  
        elif tipo_usuario == 7: # Jefe de enfermeria
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)  
        elif tipo_usuario == 8: # Medico hospitalario
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="unidad_atenc",activo=True)  

        self.fields['rolProfesionalAsignado'].queryset = UsuarioRolProfesionalAsignado.objects.filter(usuario=self.usuario)
        if tipo_usuario in [4,7]:
            self.fields["rolProfesionalAsignado"].label_from_instance = lambda obj: f"{obj.rol_profesional.tipoUsuario} ({obj.rol_profesional})"
        else:
            self.fields['rolProfesionalAsignado'].label_from_instance = lambda obj: f"{obj.rol_profesional}" 
            
        self.fields['lugar'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.abreviacion}) - Departamento: {obj.departamento}"
        self.fields['jornada'].label_from_instance = lambda obj: f"{obj.get_dia_display()} - {obj.get_turno_display()}"
        
    def clean(self):
        cleaned_data = super().clean()
        lugar = cleaned_data.get('lugar')
        jornadas = cleaned_data.get('jornada')
        usuario_inicial = self.initial.get("id_usuario")
        usuario = cleaned_data.get('id_usuario')    
        
        if not usuario:
            self.add_error(None, "Los campos deben estar completos.")            
            return cleaned_data  
        
        if not usuario_inicial:
            self.add_error(None, "Los campos deben estar completos.")            
            return cleaned_data          
        
        if str(Usuario.objects.get(pk=usuario).id) != str(usuario_inicial):
            self.add_error(None,"No está permitido cambiar el id del usuario")  
            return cleaned_data        

        if not lugar or not jornadas:
            return cleaned_data
        
        if not self.usuario:
            return cleaned_data

        if self.usuario.tipoUsuario_id in (1, 2):
            for jornada in jornadas:
                dias = []
                dias.append(jornada.dia)
                
            qs = UsuarioLugarTrabajoAsignado.objects.filter(
                usuario=self.usuario,jornada__dia__in=dias
            )
            
            if qs.exists():
                self.add_error(None,"Administración no puede tener doble turno.")
                return cleaned_data
                
        
        errores = []

        for jornada in jornadas:
            # Verificamos si el usuario ya tiene esa jornada asignada
            ya_asignado = UsuarioLugarTrabajoAsignado.objects.filter(
                usuario=self.usuario,
                jornada=jornada
            ).exists()

            if ya_asignado:
                continue  # No intentaremos asignarlo de nuevo

            # Verificamos la cantidad de usuarios asignados a ese lugar en esa jornada
            usuarios_en_jornada = UsuarioLugarTrabajoAsignado.objects.filter(
                lugar=lugar,
                jornada=jornada
            ).count()
            
            if usuarios_en_jornada >= lugar.capacidad:
                errores.append(
                    f"El lugar '{lugar.nombre} ({lugar.codigo})' ya alcanzó su capacidad máxima ({lugar.capacidad}) de usuarios asignados en la jornada: {jornada.get_dia_display()} - {jornada.get_turno_display()}."
                )

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data

    def save(self):
        lugar = self.cleaned_data['lugar']
        jornadas = self.cleaned_data['jornada']
        rolProfesional = self.cleaned_data.get('rolProfesionalAsignado')

        registros_creados = []
        jornadas_omitidas = []
        
        for jornada in jornadas:
            existe = UsuarioLugarTrabajoAsignado.objects.filter( # Validamos que el usuario no tenga asinado esa jornada
                usuario=self.usuario,
                jornada=jornada
            ).exists()
            
            if not existe:
                obj, creado = UsuarioLugarTrabajoAsignado.objects.get_or_create(
                    usuario=self.usuario,
                    rolProfesionalAsignado =rolProfesional,
                    lugar=lugar,
                    jornada=jornada
                )
                if creado:
                    registros_creados.append(obj)
            else:
                jornadas_omitidas.append(jornada)
            
        return registros_creados, jornadas_omitidas

class FormularioEditarLugarTrabajo(forms.ModelForm):
    id_instancia = forms.CharField(widget=forms.HiddenInput(attrs={"id":"id_instancia"}), required=True)    
    
    class Meta:
        model = UsuarioLugarTrabajoAsignado
        fields = ["usuario",'lugar', 'jornada','rolProfesionalAsignado']
        widgets = {
            "usuario": forms.HiddenInput(attrs={"id":"identificadorUsuarioEdit"}),
            "rolProfesionalAsignado": forms.Select(attrs={"class": "campos-modal", "id":"id_rol_edit"}),
            "lugar": forms.Select(attrs={"class": "campos-modal", "id":"id_lugar_edit"}),
            "jornada": forms.Select(attrs={"class": "campos-modal", "id":"id_jornada_edit"})
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None) 
        super().__init__(*args, **kwargs)
        
        if not self.usuario:
            raise ValueError("Se requiere un usuario para inicializar el formulario.")
        
        tipo_usuario = self.usuario.tipoUsuario.id
        
        if tipo_usuario == 1:  # Superadmin
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)  
        elif tipo_usuario == 2:  # Admin
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)  
        elif tipo_usuario == 3: # Medicos
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo__in=["cons","qui","proc"],activo=True) #Los médicos trabajan en consultorios, quirófanos y pueden realizar procedimientos ambulatorios no quirúrgicos
        elif tipo_usuario == 4: # Enfermeros
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo__in=["hab","unidad_atenc"],activo=True)  # Los enfermeros se desempeñan principalmente en internación y unidades de atención
        elif tipo_usuario == 5: # Apoyo en Diagnóstico y Tratamiento (Radiologos,ecografista,tecnico en laboratorio , etc  )
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo__in=["lab", "img","diag_func","unidad_atenc","proc"], activo=True)  # Laboratorios 
        elif tipo_usuario == 6: # Cargador de resultados
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)  
        elif tipo_usuario == 7: # Jefe de enfermeria
            self.fields['lugar'].queryset = Lugar.objects.filter(tipo="area_apoyo",activo=True)  

        self.fields['rolProfesionalAsignado'].queryset = UsuarioRolProfesionalAsignado.objects.filter(usuario=self.usuario)
        if tipo_usuario in [4,7]:
            self.fields["rolProfesionalAsignado"].label_from_instance = lambda obj: f"{obj.rol_profesional.tipoUsuario} ({obj.rol_profesional})"
        else:
            self.fields['rolProfesionalAsignado'].label_from_instance = lambda obj: f"{obj.rol_profesional}" 
        
        self.fields['lugar'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.abreviacion}) - Departamento: {obj.departamento}"
        self.fields['jornada'].label_from_instance = lambda obj: f"{obj.get_dia_display()} - {obj.get_turno_display()}"

    def clean(self):
        cleaned_data = super().clean()
        lugar = cleaned_data.get("lugar")
        jornada = cleaned_data.get("jornada")
        usuario_inicial = self.initial.get("usuario")
        usuario = cleaned_data.get('usuario')    
        
        if not usuario:
            self.add_error(None, "Los campos deben estar completos.")            
            return cleaned_data  
        
        if not usuario_inicial:
            self.add_error(None, "Los campos deben estar completos.")            
            return cleaned_data          
        
        if str(usuario.id) != str(usuario_inicial):
            self.add_error(None,"No está permitido cambiar el id del usuario")  
            return cleaned_data          
        
        if not lugar or not jornada:
            return cleaned_data
        
        
        if self.usuario.tipoUsuario_id in (1, 2): 
            qs = UsuarioLugarTrabajoAsignado.objects.filter(
                usuario=self.usuario,jornada__dia=jornada.dia
            )
            
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
                
            
            if qs.exists():
                self.add_error(None,"Administración no puede tener doble turno.")
                return cleaned_data
              

        # Validación de jornada duplicada
        if self.instance.pk:
            conflicto = UsuarioLugarTrabajoAsignado.objects.filter(
                usuario=self.usuario,
                jornada=jornada
            ).exclude(pk=self.instance.pk).exists()
            if conflicto:
                self.add_error("jornada", "Este usuario ya tiene asignada esa jornada en otro lugar.")

        # Validación de capacidad del lugar
        asignaciones = UsuarioLugarTrabajoAsignado.objects.filter(lugar=lugar,jornada=jornada)
        if self.instance.pk:
            asignaciones = asignaciones.exclude(pk=self.instance.pk)

        if asignaciones.count() >= lugar.capacidad:
            self.add_error("lugar", f"El lugar '{lugar.nombre}' ya alcanzó su capacidad máxima de {lugar.capacidad} usuarios.")

        return cleaned_data





class FormularioAsignaciones(forms.ModelForm): 
    id_instancia = forms.CharField(widget=forms.HiddenInput(attrs={"id":"id_asignacion"}), required=False)    
    
    class Meta:
        model = UsuarioRolProfesionalAsignado 
        fields = [ # Acá ingresamos los campos que queremos que se muestren en el formulario.
            "usuario",'rol_profesional'
        ]
        widgets = {
            "usuario" : forms.HiddenInput(),
            "rol_profesional" : forms.Select(attrs={"class":"campos-modal"}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
                
        tipo_usuario = self.user.tipoUsuario.id
        
        # Roles ya asignados al usuario
        roles_asignados = UsuarioRolProfesionalAsignado.objects.filter(usuario=self.user).values_list('rol_profesional_id', flat=True)

        # Excluir los roles ya asignados
        if tipo_usuario == 3: # Medico
            self.fields['rol_profesional'].queryset = RolesProfesionales.objects.filter(tipoUsuario_id=tipo_usuario,especialidad__permite_turno=True).exclude(id__in=roles_asignados)
        else:
            self.fields['rol_profesional'].queryset = RolesProfesionales.objects.filter(tipoUsuario_id=tipo_usuario).exclude(id__in=roles_asignados)
        
        if tipo_usuario in [4,7]:
            self.fields["rol_profesional"].label_from_instance = lambda obj: f"{obj.tipoUsuario} ({obj.nombre_rol_profesional})"
        else:
            self.fields['rol_profesional'].label_from_instance = lambda obj: f"{obj.nombre_rol_profesional}"     
    
    def clean(self):
        cleaned_data = super().clean()
        usuario_inicial = self.initial.get("usuario")
        usuario = cleaned_data.get('usuario')    

        if not usuario:
            self.add_error(None, "Los campos deben estar completos.")            
            return cleaned_data  
        
        if not usuario_inicial:
            self.add_error(None, "Los campos deben estar completos.")            
            return cleaned_data          
        
        if str(usuario.id) != str(usuario_inicial):
            self.add_error(None,"No está permitido cambiar el id del usuario")  
            return cleaned_data        

        if usuario.tipoUsuario_id in (1, 2):
            qs = UsuarioRolProfesionalAsignado.objects.filter(usuario=usuario)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error(None, "Administración no puede tener más de un rol asignado.")
                return cleaned_data
                

        return cleaned_data



    

    



class FormConsulta(forms.ModelForm):
    class Meta:
        model = Consultas
        fields = ['diagnostico', 'tratamiento', 'observaciones']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, "placeholder":"Diagnóstico principal..."}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, "placeholder":"Hallazgos, examen físico, evolución..."}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, "placeholder":"Recomendaciones, dieta, actividad..."})
        }

class FormEstudio(forms.ModelForm):
    class Meta:
        model = OrdenEstudio
        fields = ['tipo_estudio', "motivo_estudio","indicaciones"]
        widgets = {
            'motivo_estudio': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Sospecha de...'}),
            'indicaciones': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Ej. En ayunas'}),
        }
    
    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs)
        self.fields['tipo_estudio'].label_from_instance = lambda obj: obj.nombre_estudio # Esto hace que en el <select> aparezca siempre nombre_estudio, sin importar el __str__.
    
    # Hacer los campos opcionales
    tipo_estudio = forms.ModelChoiceField(
        queryset=EstudiosDiagnosticos.objects.all(),
        required=False,
        widget=forms.Select()
    )
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_estudio')
        motivo = cleaned_data.get('motivo_estudio')
        indicaciones = cleaned_data.get('indicaciones')

        # Validación condicional: si se completa algún campo, los demás son requeridos
        if tipo or motivo or indicaciones:
            if not tipo:
                self.add_error('tipo_estudio', 'Este campo es obligatorio si se completan otros.')
            if not motivo:
                self.add_error('motivo_estudio', 'Este campo es obligatorio si se completan otros.')
            if not indicaciones:
                self.add_error('indicaciones', 'Este campo es obligatorio si se completan otros.')

class FormMedicacion(forms.ModelForm):
    class Meta:
        model = Medicaciones
        fields = ['medicamento', 'dosis', 'frecuencia', 'tiempo_uso']
        widgets = {
            'medicamento': forms.TextInput(attrs={'placeholder': 'Ej: Paracetamol'}),
            'dosis': forms.TextInput(attrs={'placeholder': 'Ej: 500mg'}),
            'frecuencia': forms.TextInput(attrs={'placeholder': 'Ej: Cada 8 horas'}),
            'tiempo_uso': forms.TextInput(attrs={'placeholder': 'Ej: usuar durante 7 dias'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        medicamento = cleaned_data.get('medicamento')
        dosis = cleaned_data.get('dosis')
        frecuencia = cleaned_data.get('frecuencia')
        tiempo_uso = cleaned_data.get('tiempo_uso')

        if medicamento or dosis or frecuencia or tiempo_uso:
            if not medicamento:
                self.add_error('medicamento', 'Este campo es obligatorio si se completan otros.')
            if not dosis:
                self.add_error('dosis', 'Este campo es obligatorio si se completan otros.')
            if not frecuencia:
                self.add_error('frecuencia', 'Este campo es obligatorio si se completan otros.')
            if not tiempo_uso:
                self.add_error('tiempo_uso', 'Este campo es obligatorio si se completan otros.')

# Permite agregar múltiples estudios por consulta
EstudiosFormSet = modelformset_factory(
    OrdenEstudio, 
    form=FormEstudio,
    extra=1,  # indica que por defecto se muestra 1 formulario vacío. Cambialo a 2 o 3 si querés que aparezcan más.
    can_delete=True  # agrega una opción para eliminar formularios en el template (útil para descartar una línea).
)

# Permite agregar múltiples medicaciones por consulta
MedicacionesFormSet = modelformset_factory(
    Medicaciones,
    form=FormMedicacion,
    extra=1,
    can_delete=True
)

class ResultadoEstudioForm(forms.ModelForm):
    class Meta:
        model = ResultadoEstudio
        fields = ["informe"]  # solo informe fijo, los demás campos se agregan dinámicamente
        widgets = {
            "informe": forms.Textarea(attrs={"rows": 5,"placeholder":"Escribe el informe aquí si corresponde..."}),
        }
        
    def __init__(self, *args, **kwargs):
        self.turno = kwargs.pop("turno", None)
        super().__init__(*args, **kwargs)

        self.estructura = {}  # guardamos para usar luego en save()
        if self.turno:
            plantilla = getattr(self.turno.orden.tipo_estudio, "plantilla", None)
            if plantilla:
                self.estructura = plantilla.estructura.get(self.turno.orden.tipo_estudio.nombre_estudio, {})
                tipo = self.turno.orden.tipo_estudio.tipo_resultado
                if tipo == "lab":
                    # Generar dinámicamente un campo para cada parámetro del estudio
                    for parametro, detalles in self.estructura.items():
                        self.fields[parametro] = forms.CharField( # Creamos un campo para el valor de cada parámetro
                            label=f'Nombre: {parametro} - Unidad: {detalles.get("unidad","")} - Rango de referencia: {detalles.get("referencia","")}',
                            required=False,
                            widget=forms.TextInput(attrs={"placeholder": f"Ingrese valor de {parametro}"})
                        ) 
                elif tipo == "fisio":
                    for parametro, detalles in self.estructura.items():
                        self.fields[f"{parametro}_valor"] = forms.CharField(
                                label=f'Nombre: {parametro} - Unidad: {detalles.get("unidad","")} - Referencia: {detalles.get("referencia","")}',                               
                                required=False,
                                widget=forms.TextInput(attrs={"placeholder": f"Ingrese valor de {parametro}"})
                            )
                        self.fields[f"{parametro}_interpretacion"] = forms.CharField(
                            required=False,
                            widget=forms.TextInput(attrs={"placeholder": f"Ingrese interpretación de {parametro}"})
                        )
            
    def save(self, commit=True):
        instance = super().save(commit=False)

        datos = {}
        tipo = self.turno.orden.tipo_estudio.tipo_resultado

        for parametro, detalles in self.estructura.items():
            if tipo == "lab":
                valor = self.cleaned_data.get(parametro, "")
                datos[parametro] = {
                    "valor": valor,
                    "unidad": detalles.get("unidad", ""),
                    "referencia": detalles.get("referencia", "")
                }
            elif tipo == "fisio":
                valor = self.cleaned_data.get(f"{parametro}_valor", "")
                interpretacion = self.cleaned_data.get(f"{parametro}_interpretacion", "")
                datos[parametro] = {
                    "valor": valor,
                    "unidad": detalles.get("unidad", ""),
                    "referencia": detalles.get("referencia", ""),
                    "interpretacion": interpretacion
                }

        instance.datos_especificos = datos
        if commit:
            instance.save()
        return instance


class ResultadoImagenForm(forms.ModelForm):
    class Meta:
        model = ResultadoImagen
        fields = ["imagen"] 



class FormSacarTurno(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['fecha_turno', 'horario_turno', 'motivo', 'lugar','especialidad','paciente','profesional']
        widgets = {
            'motivo': forms.Textarea(attrs={'placeholder': 'Motivo del turno...', "class":"textarea-motivo-turno","cols":"0","rows":"0"}),
            'especialidad': forms.HiddenInput(),
            'profesional': forms.HiddenInput(),
            'paciente': forms.HiddenInput(),
            'fecha_turno': forms.HiddenInput(),
            'horario_turno': forms.HiddenInput(),
            'lugar': forms.HiddenInput()
        }
    
    def clean_fecha_turno(self):
        fecha = self.cleaned_data.get('fecha_turno')
        if fecha <= datetime.date.today():
            raise forms.ValidationError("No se puede seleccionar una fecha pasada.")
        return fecha    

class FormSacarTurnoEstudio(forms.ModelForm):
    class Meta:
        model = TurnoEstudio
        fields = ['fecha_turno', 'horario_turno', 'lugar','orden','servicio_diagnostico']
        widgets = {
            'orden': forms.HiddenInput(),
            'servicio_diagnostico': forms.HiddenInput(),
            'fecha_turno': forms.HiddenInput(attrs={"id": "fecha_seleccionada"}),
            'horario_turno': forms.HiddenInput(),
            'lugar': forms.HiddenInput()
        }
    
    def clean_fecha_turno(self):
        fecha = self.cleaned_data.get('fecha_turno')
        if fecha <= datetime.date.today():
            raise forms.ValidationError("No se puede seleccionar una fecha pasada.")
        return fecha    


class FormularioAsignarHabitacion(forms.ModelForm): 
    lugar = forms.ModelChoiceField(
        queryset=Lugar.objects.filter(tipo="hab"),
        widget=forms.RadioSelect(attrs={"class": "box-radio"}),
        label="Habitaciones"
    )
    
    class Meta:
        model = AsignacionesHabitaciones 
        fields = [ 
            'paciente',"lugar"
        ]
        widgets = {
            "paciente" : forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lugares = Lugar.objects.filter(tipo="hab").annotate(
            cantidadActual=Count('asignacioneshabitaciones')
        )
        self.fields["lugar"].queryset = lugares
        
        self.fields['lugar'].label_from_instance = lambda obj:(
            f"{obj.nombre} ({obj.abreviacion}) - Departamento: {obj.departamento} - "+ (f"Capacidad: ({obj.cantidadActual}/{obj.capacidad})" if obj.activo==True else "Inactivo")
        )
    
    def clean(self):
        cleaned_data = super().clean()
        paciente_inicial = self.initial.get("paciente")
        paciente = cleaned_data.get('paciente')
        lugar = cleaned_data.get("lugar")
        instancia = self.instance
        es_edicion = instancia.pk is not None
        
        if not paciente_inicial:
            return cleaned_data          
        
        if not lugar:
            return cleaned_data
        
        if not paciente:
            return cleaned_data
        
        if str(paciente.id) != str(paciente_inicial):
            self.add_error(None,"No está permitido cambiar el id del paciente")  
            return cleaned_data
            
        if paciente.persona.is_active == False:
            self.add_error(None,"El paciente está inactivo")  
            return cleaned_data    
        
        if not es_edicion:
            if AsignacionesHabitaciones.objects.filter(paciente=paciente).exists():
                self.add_error(None, 'Este paciente ya esta asignado a una habitación.')
                return cleaned_data
        
        
        if lugar.activo == False:
            self.add_error("lugar", 'Este lugar esta inactivo.')
            
        capacidadMax = lugar.capacidad
        if AsignacionesHabitaciones.objects.filter(lugar=lugar,estado="activa").count() >= capacidadMax:
            self.add_error("lugar", 'Este lugar no tiene disponibilidad o esta inactivo.')
        
        
        return cleaned_data
    

            

class FormularioAsignarMedicoTratante(forms.ModelForm): 
    medico = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(tipoUsuario_id=8), # Medicos hospitalarios  (agregar el ,persona__is_active=True luego)
        widget=autocomplete.ModelSelect2(url='medico-tratante-autocomplete',attrs={"class": "campos-modal","data-placeholder": "Buscar médico hospitalario por nombre, apellido, n° matricula o especialidad..."}),
        label="Médico hospitalario"
    )
    
    class Meta:
        model = AsignacionMedico 
        fields = [ 
            'asignacion_habitacion',"medico"
        ]
        widgets = {
            "asignacion_habitacion" : forms.HiddenInput()
        }
        
        
    
    def clean(self):
        cleaned_data = super().clean()        
        asignacionHabitacion = cleaned_data.get('asignacion_habitacion')
        asignacion_inicial = self.initial.get("asignacion_habitacion")
        medico = cleaned_data.get('medico')
        
        if not asignacion_inicial:
            return cleaned_data        
        
        if not asignacionHabitacion:
            return cleaned_data
        
        if not medico:
            return cleaned_data
        
        if str(asignacionHabitacion.id) != str(asignacion_inicial):
            self.add_error(None,"No está permitido cambiar el id de registro de habitación asignada")      
            return cleaned_data
        
        return cleaned_data


class FormularioAsignarEnfermero(forms.ModelForm): 
    enfermero = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        widget=autocomplete.ModelSelect2(
            url='enfermero-autocomplete',
            forward=["jornada"],  
            attrs={
                "class": "campos-modal",
                "data-placeholder": "Buscar enfermero por nombre, apellido, n° matricula o especialidad..."
            }
        ),
        label="Enfermero:"
    )

    class Meta:
        model = AsignacionEnfermero
        fields = ["asignacion_habitacion",'jornada', 'enfermero']
        widgets = {
            "asignacion_habitacion": forms.HiddenInput(),
            "jornada": forms.HiddenInput()
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        jornada = None

        # Si el form está recibiendo data (POST)
        if "jornada" in self.data:
            try:
                jornada = int(self.data.get("jornada"))
            except (ValueError, TypeError):
                pass
        
        elif self.instance.pk:
            jornada = self.instance.jornada_id
            
        if jornada:
            self.fields["enfermero"].queryset = Usuario.objects.filter(
                tipoUsuario_id=4,
                UsuariosAsignadosAEsteLugar__jornada__id=jornada
            )        
        
    def clean(self):
        cleaned_data = super().clean()        
        asignacionHabitacion = cleaned_data.get('asignacion_habitacion')
        asignacion_inicial = self.initial.get("asignacion_habitacion")
        enfermero = cleaned_data.get('enfermero')
        jornada = cleaned_data.get('jornada')

        if not asignacion_inicial:
            return cleaned_data        
        
        if not asignacionHabitacion:
            return cleaned_data
        
        if not jornada:
            return cleaned_data
        
        if not enfermero:
            return cleaned_data
        
        if str(asignacionHabitacion.id) != str(asignacion_inicial):
            self.add_error(None,"No está permitido cambiar el id de registro de habitación asignada.")      
            return cleaned_data
        
        if not self.instance.pk:
            if AsignacionEnfermero.objects.filter(pk=asignacionHabitacion.id,jornada=jornada).exists():
                self.add_error(None,"Ya hay un enfermero asignado a esa jornada.")      
                return cleaned_data
        
        if self.instance.pk:
            if self.instance.jornada != jornada:
                self.add_error(None,"La asignacion de enfermero no coincide con la jornada.")      
                return cleaned_data
            
            if self.instance.enfermero == enfermero:
                self.add_error("enfermero","No puedes seleccionar el mismo enfermero")
                return cleaned_data
        
        
        return cleaned_data


class FormularioEvaluacionMedica(forms.ModelForm): 
    class Meta:
        model = ObservacionesMedico
        fields = ["asignacion_medico","motivo",'diagnostico', 'evolucion_clinica',"indicaciones"]
        widgets = {
            "asignacion_medico": forms.HiddenInput(),
            "motivo": forms.Textarea(attrs={"placeholder":"Motivo de ingreso","cols":"0","rows":"0"}),
            "diagnostico": forms.Textarea(attrs={"placeholder":"Diagnóstico médico","cols":"0","rows":"0"}),
            "evolucion_clinica": forms.Textarea(attrs={"placeholder":"Evolución clínica","cols":"0","rows":"0"}),
            "indicaciones": forms.Textarea(attrs={"placeholder":"Indicaciones para enfermería","cols":"0","rows":"0"})
        }
        labels = {
            "motivo": "Motivo de ingreso",
            "diagnostico": "Diagnóstico médico",
            "evolucion_clinica": "Evolución clínica",
            "indicaciones": "Indicaciones para enfermería"
        }
    
    def __init__(self, *args, readonly=False, **kwargs):
        super().__init__(*args, **kwargs)
        if readonly:
            for field in self.fields.values():
                field.widget.attrs["readonly"] = True
            
        
    def clean(self):
        cleaned_data = super().clean()        
        asignacionMedico = cleaned_data.get('asignacion_medico')
        asignacionMedico_inicial = self.initial.get("asignacion_medico")    
        motivo = cleaned_data.get('motivo')
        
        if not asignacionMedico_inicial:
            return cleaned_data        
        
        if not asignacionMedico:
            self.add_error(None,"No existe un registro con ese valor en asignacion medico")      
            return cleaned_data            
        
        if str(asignacionMedico.id) != str(asignacionMedico_inicial):
            self.add_error(None,"No está permitido cambiar el id de la asignacion de medico.")      
            return cleaned_data
        
        if ObservacionesMedico.objects.filter(asignacion_medico=asignacionMedico).exists():
            observacionMedico = ObservacionesMedico.objects.filter(asignacion_medico=asignacionMedico).order_by("-id").first()
            if motivo != observacionMedico.motivo:
                self.add_error("motivo","No puedes modificar el campo motivo")      
                return cleaned_data
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        ultimo = ObservacionesMedico.objects.filter(asignacion_medico=instance.asignacion_medico).order_by('-id').first()
        if ultimo:
            instance.motivo = ultimo.motivo # Manterner siempre el mismo valor en el campo motivo.
        
        if commit:
            instance.save()
        return instance


class FormularioNotaEnfermo(forms.ModelForm): 
    class Meta:
        model = ObservacionesEnfermero
        fields = ["asignacion_enfermero","observaciones",'signos_vitales', 'procedimientos_realizados',"medicacion_administrada"]
        widgets = {
            "asignacion_enfermero": forms.HiddenInput(),
            "observaciones": forms.Textarea(attrs={"placeholder":"Describa el estado general del paciente, cambios observados, conducta, respuesta al tratamiento, etc.","cols":"0","rows":"0"}),
            "signos_vitales": forms.Textarea(attrs={"placeholder":"Registrar TA, FC, FR, SatO2, T°, Glasgow u otros parámetros relevantes.","cols":"0","rows":"0"}),
            "procedimientos_realizados": forms.Textarea(attrs={"placeholder":"Detalle procedimientos realizados (curaciones, movilización, higiene, instalación de vías, etc.).","cols":"0","rows":"0"}),
            "medicacion_administrada": forms.Textarea(attrs={"placeholder":"Indique medicación administrada: nombre, dosis, vía, horario y respuesta del paciente.","cols":"0","rows":"0"})
        }
        labels = {
            "observaciones": "Observaciones de Enfermería",
            "signos_vitales": "Signos Vitales",
            "procedimientos_realizados": "Procedimientos Realizados (opcional)",
            "medicacion_administrada": "Medicación Administrada (opcional)"
        }
    
        
    def clean(self):
        cleaned_data = super().clean()        
        asignacionEnfermero = cleaned_data.get('asignacion_enfermero')
        asignacionEnfermero_inicial = self.initial.get("asignacion_enfermero")    
        
        if not asignacionEnfermero_inicial:
            return cleaned_data        
        
        if not asignacionEnfermero:
            self.add_error(None,"No existe un registro con ese valor en asignacion enfermero")      
            return cleaned_data            
        
        if str(asignacionEnfermero.id) != str(asignacionEnfermero_inicial):
            self.add_error(None,"No está permitido cambiar el id de la asignacion de enfermero.")      
            return cleaned_data
        
        
        return cleaned_data



class FormularioAltaMedica(forms.ModelForm): 
    class Meta:
        model = AltaMedica
        fields = ["asignacion_medico","diagnostico_principal","diagnosticos_secundarios",'tratamiento_realizado', 'indicaciones_post_alta']
        widgets = {
            "asignacion_medico": forms.HiddenInput(),
            "diagnostico_principal": forms.Textarea(attrs={"placeholder":"Resuma el diagnóstico principal que motivó la hospitalización o atención, evolución clínica y estado actual al momento del alta.","cols":"0","rows":"0"}),
            "diagnosticos_secundarios": forms.Textarea(attrs={"placeholder":"Consigne diagnósticos asociados, comorbilidades o complicaciones relevantes identificadas durante la atención (opcional).","cols":"0","rows":"0"}),
            "tratamiento_realizado": forms.Textarea(attrs={"placeholder":"Describa los tratamientos efectuados: procedimientos, intervenciones, medicación administrada y respuesta del paciente.","cols":"0","rows":"0"}),
            "indicaciones_post_alta": forms.Textarea(attrs={"placeholder":"Indique las recomendaciones al alta: medicación prescrita (dosis, horario, vía), cuidados domiciliarios, controles sugeridos y signos de alarma (opcional).","cols":"0","rows":"0"})
        }
        labels = {
            "diagnostico_principal": "Diagnostico Principal",
            "diagnosticos_secundarios": "Diagnosticos Secundarios (opcional)",
            "tratamiento_realizado": "Tratamiento Realizado",
            "indicaciones_post_alta": "Indicaciones Post Alta (opcional)"
        }
    
        
    def clean(self):
        cleaned_data = super().clean()        
        asignacionMedico = cleaned_data.get('asignacion_medico')
        asignacionMedico_inicial = self.initial.get("asignacion_medico")    
        
        if not asignacionMedico_inicial:
            return cleaned_data        
        
        if not asignacionMedico:
            self.add_error(None,"No existe un registro con ese valor en asignacion medico")      
            return cleaned_data            
        
        if str(asignacionMedico.id) != str(asignacionMedico_inicial):
            self.add_error(None,"No está permitido cambiar el id de la asignacion medica.")      
            return cleaned_data
        
        
        return cleaned_data


class FormularioAltaAdministrativa(forms.Form):
    paciente_id = forms.CharField(widget=forms.HiddenInput())
    asignacionHabitacion_id = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        paciente_id = cleaned_data.get('paciente_id')
        asignacionHabitacion_id = cleaned_data.get('asignacionHabitacion_id')

        paciente_inicial = self.initial.get("paciente_id")
        asignacionHabitacion_inicial = self.initial.get("asignacionHabitacion_id")

        if not paciente_inicial or not asignacionHabitacion_inicial:
            return cleaned_data

        if not paciente_id or not asignacionHabitacion_id:
            self.add_error(None, "Los campos deben estar completos.")
            return cleaned_data

        if str(paciente_id) != str(paciente_inicial):
            self.add_error(None, "No está permitido cambiar el id del paciente.")
            return cleaned_data

        if str(asignacionHabitacion_id) != str(asignacionHabitacion_inicial):
            self.add_error(None, "No está permitido cambiar la asignación de habitación.")
            return cleaned_data

        return cleaned_data
    
class FormularioCancelarAsignacionHabitacion(forms.Form):
    asignacionHabitacion_id = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        asignacionHabitacion_id = cleaned_data.get('asignacionHabitacion_id')

        asignacionHabitacion_inicial = self.initial.get("asignacionHabitacion_id")

        if not asignacionHabitacion_inicial:
            return cleaned_data

        if not asignacionHabitacion_id:
            self.add_error(None, "Los campos deben estar completos.")
            return cleaned_data

        if str(asignacionHabitacion_id) != str(asignacionHabitacion_inicial):
            self.add_error(None, "No está permitido cambiar la asignación de habitación.")
            return cleaned_data
        
        if AsignacionMedico.objects.filter(asignacion_habitacion_id=asignacionHabitacion_id).exists():
            self.add_error(None, "No puedes cancelar esta asignacion porque ya tiene un medico asignado.")
            return cleaned_data

        return cleaned_data



