import django_filters
from .models import Lugar,Departamento,Especialidades,ServicioDiagnostico,EstudiosDiagnosticos,PlantillaEstudio,AsignacionMedico,AsignacionEnfermero,ObservacionesEnfermero,Jorna_laboral,UsuarioLugarTrabajoAsignado,ObservacionesMedico,UsuarioRolProfesionalAsignado,Consultas
from hospital_pacientes.models import Paciente
from controlUsuario.models import Usuario,TiposUsuarios,RolesProfesionales
from django import forms
from django.utils import timezone
from datetime import datetime,time

class UsuarioFilter(django_filters.FilterSet):
    persona__login_id = django_filters.CharFilter(
        field_name='persona__login_id',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='N° Legajo:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por el N° Legajo...'})
    )    
    tipoUsuario = django_filters.ModelChoiceFilter(
        queryset=TiposUsuarios.objects.all(),
        label='Tipo usuario:',
        empty_label='-- Sin filtros --',  
    )
    numero_matricula = django_filters.NumberFilter(
        field_name='numero_matricula',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='N° Matricula:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por el N° Matricula...'})
    )   
    persona__first_name = django_filters.CharFilter(
        field_name='persona__first_name',
        lookup_expr='icontains',
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    persona__last_name = django_filters.CharFilter(
        field_name='persona__last_name',
        lookup_expr='icontains',
        label='Apellido:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    
    persona__is_active = django_filters.BooleanFilter(
        field_name='persona__is_active',
        label='Estado:',
        widget=forms.Select(choices=[('', '-- Sin filtros --'), ('True', 'Activo'), ('False', 'Inactivo')])
    )
    
    class Meta:
        model = Usuario
        fields = [
            'persona__login_id',  
            'tipoUsuario',  
            'numero_matricula',  
            'persona__first_name', 
            'persona__last_name', 
            'persona__is_active' 
        ]

class UsuariosNoAdministracionFilter(django_filters.FilterSet):
    persona__login_id = django_filters.CharFilter(
        field_name='persona__login_id',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='N° Legajo:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por el N° Legajo...'})
    )    
    tipoUsuario = django_filters.ModelChoiceFilter(
        queryset=TiposUsuarios.objects.exclude(pk__in=[1,2]),
        label='Tipo usuario:',
        empty_label='-- Sin filtros --',  
    )
    numero_matricula = django_filters.NumberFilter(
        field_name='numero_matricula',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='N° Matricula:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por el N° Matricula...'})
    )   
    persona__first_name = django_filters.CharFilter(
        field_name='persona__first_name',
        lookup_expr='icontains',
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    persona__last_name = django_filters.CharFilter(
        field_name='persona__last_name',
        lookup_expr='icontains',
        label='Apellido:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    
    
    class Meta:
        model = Usuario
        fields = [
            'persona__login_id',  
            'tipoUsuario',  
            'numero_matricula',  
            'persona__first_name', 
            'persona__last_name', 
        ]

class EspecialidadesFilter(django_filters.FilterSet):
    nombre_especialidad = django_filters.CharFilter(
        field_name='nombre_especialidad',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre...'})
    )    
    departamento = django_filters.ModelChoiceFilter(
        queryset=Departamento.objects.all(),
        label='Departamento:',
        empty_label='-- Sin filtros --',  
    )
    permite_turno = django_filters.BooleanFilter(
        field_name='permite_turno',
        label='Permite turno:',
        widget=forms.Select(choices=[('', '-- Sin filtros --'), ('True', 'Sí'), ('False', 'No')])
    )
    
    class Meta:
        model = Especialidades
        fields = [
            'nombre_especialidad',  
            'departamento',  
            "permite_turno"
        ]

class ServiciosFilter(django_filters.FilterSet):
    nombre_servicio = django_filters.CharFilter(
        field_name='nombre_servicio',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre...'})
    )    
    departamento = django_filters.ModelChoiceFilter(
        queryset=Departamento.objects.all(),
        label='Departamento:',
        empty_label='-- Sin filtros --',  
    )
    lugar = django_filters.ModelChoiceFilter(
        field_name='lugar',
        queryset=Lugar.objects.filter(tipo__in=["lab", "img","diag_func","unidad_atenc","proc"]),
        label='Lugar:',
        empty_label='-- Sin filtros --',  
    )
    
    class Meta:
        model = ServicioDiagnostico
        fields = [
            'nombre_servicio',  
            'departamento',  
            "lugar"
        ]

class EstudiosFilter(django_filters.FilterSet):
    nombre_estudio = django_filters.CharFilter(
        field_name='nombre_estudio',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre...'})
    )    
    tipo_resultado = django_filters.ChoiceFilter(
        field_name='tipo_resultado',
        choices=EstudiosDiagnosticos.TIPO_CHOICES,
        label='Tipo de resultado:',
        empty_label='-- Sin filtros --',  
    )    
    servicio_diagnostico = django_filters.ModelChoiceFilter(
        field_name='servicio_diagnostico',
        queryset=ServicioDiagnostico.objects.all(),
        label='Servicio de diagnostico encargado:',
        empty_label='-- Sin filtros --',  
    )
    
    class Meta:
        model = EstudiosDiagnosticos
        fields = [
            'nombre_estudio',  
            'tipo_resultado',  
            "servicio_diagnostico"
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        servicio_diagnostico_field = self.form.fields['servicio_diagnostico']
        servicio_diagnostico_field.label_from_instance = (
            lambda obj: f"{obj.nombre_servicio}"
        )

class PlantillaEstudioFilter(django_filters.FilterSet):
    estudio__nombre_estudio = django_filters.CharFilter(
        field_name='estudio__nombre_estudio',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre...'})
    )    
    
    class Meta:
        model = PlantillaEstudio
        fields = [
            'estudio__nombre_estudio',  
        ]

class RolesProfesionalesFilter(django_filters.FilterSet):
    nombre_rol_profesional = django_filters.CharFilter(
        field_name='nombre_rol_profesional',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre...'})
    )    
    tipoUsuario = django_filters.ModelChoiceFilter(
        field_name='tipoUsuario',
        queryset=TiposUsuarios.objects.all(),
        label='Tipo usuario:',
        empty_label='-- Sin filtros --',  
    )
    
    class Meta:
        model = PlantillaEstudio
        fields = [
            'nombre_rol_profesional',  
            "tipoUsuario"
        ]

class DepartamentosFilter(django_filters.FilterSet):
    nombre_departamento = django_filters.CharFilter(
        field_name='nombre_departamento',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre...'})
    )    
    
    class Meta:
        model = Departamento
        fields = [
            'nombre_departamento',  
        ]




class LugarFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        field_name='nombre',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )    
    piso = django_filters.NumberFilter(
        field_name='piso',
        lookup_expr='exact',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Piso:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por N° de piso...'})
    )    
    sala = django_filters.NumberFilter(
        field_name='sala',
        lookup_expr='exact',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='Sala:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por N° de sala...'})
    )    
    es_critico = django_filters.BooleanFilter(
        field_name='es_critico',
        label='Es critico:',
        widget=forms.Select(choices=[('', '-- Sin filtros --'), ('True', 'Sí'), ('False', 'No')])
    )
    activo = django_filters.BooleanFilter(
        field_name='activo',
        label='Esta activo:',
        widget=forms.Select(choices=[('', '-- Sin filtros --'), ('True', 'Sí'), ('False', 'No')])
    )
    departamento = django_filters.ModelChoiceFilter(
        queryset=Departamento.objects.all(),
        label='Departamento',
        empty_label='-- Sin filtros --',  
    )
    
    class Meta:
        model = Lugar
        fields = [
            'nombre',  
            'tipo',  
            'piso',  
            'sala', 
            'es_critico', 
            'activo',  
            'departamento',  
        ]
    

class PacienteFilter(django_filters.FilterSet):
    persona__dni = django_filters.CharFilter(
        field_name='persona__dni',
        lookup_expr='icontains',
        label='DNI:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el DNI...'})
    )
    persona__first_name = django_filters.CharFilter(
        field_name='persona__first_name',
        lookup_expr='icontains',
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    persona__last_name = django_filters.CharFilter(
        field_name='persona__last_name',
        lookup_expr='icontains',
        label='Apellido:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    
    persona__is_active = django_filters.BooleanFilter(
        field_name='persona__is_active',
        label='Estado:',
        widget=forms.Select(choices=[('', '-- Sin filtros --'), ('True', 'Activo'), ('False', 'Inactivo')])
    )
    
    RESPONSABLE_CHOICES = (
        ('', '-- Sin filtros --'),
        ('titular', 'Titular'),
        ('menor', 'Menor'),
    )
    
    responsable = django_filters.ChoiceFilter(
        choices=RESPONSABLE_CHOICES,
        method='filter_responsable',  # usamos un método custom
        label='Tipo paciente:',
        empty_label=None
    )    
    
    class Meta:
        model = Paciente
        fields = [
            'persona__dni',
            'persona__first_name',
            'persona__last_name',
            'persona__is_active',
            'responsable'
        ]
        
    def filter_responsable(self, queryset, name, value):  # Método custom que aplica el filtro
        if value == 'menor':
            return queryset.filter(responsable__isnull=False)
        elif value == 'titular':
            return queryset.filter(responsable__isnull=True)
        return queryset


class BasePacienteAsignadosHabitacionFilter(django_filters.FilterSet):
    asignacion_habitacion__paciente__persona__dni = django_filters.CharFilter(
        lookup_expr='icontains',
        label='DNI:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por DNI...'})
    )

    asignacion_habitacion__paciente__persona__first_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre...'})
    )

    asignacion_habitacion__paciente__persona__last_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Apellido:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por apellido...'})
    )

    asignacion_habitacion__lugar = django_filters.ModelChoiceFilter(
        queryset=Lugar.objects.filter(tipo="hab"),
        label='Lugar',
        empty_label='-- Sin filtros --',
    )

    class Meta:
        fields = [
            'asignacion_habitacion__paciente__persona__dni',
            'asignacion_habitacion__paciente__persona__first_name',
            'asignacion_habitacion__paciente__persona__last_name',
            'asignacion_habitacion__lugar',
        ]

class PacientesAsignadosHabitacionMedicoFilter(BasePacienteAsignadosHabitacionFilter):
    class Meta(BasePacienteAsignadosHabitacionFilter.Meta):
        model = AsignacionMedico

class PacientesAsignadosHabitacionEnfermeroFilter(BasePacienteAsignadosHabitacionFilter):
    class Meta(BasePacienteAsignadosHabitacionFilter.Meta):
        model = AsignacionEnfermero



class ObservacionesDeEnfermerosFilter(django_filters.FilterSet):
    asignacion_enfermero__enfermero__numero_matricula = django_filters.CharFilter(
        field_name='asignacion_enfermero__enfermero__numero_matricula',
        lookup_expr='icontains',
        label='Matricula enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por N° Matricula...'})
    )
    asignacion_enfermero__enfermero__persona__first_name = django_filters.CharFilter(
        field_name='asignacion_enfermero__enfermero__persona__first_name',
        lookup_expr='icontains',
        label='Nombre enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    asignacion_enfermero__enfermero__persona__last_name = django_filters.CharFilter(
        field_name='asignacion_enfermero__enfermero__persona__last_name',
        lookup_expr='icontains',
        label='Apellido enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    unique_turnos = (
        Jorna_laboral.objects
        .values_list("turno", flat=True)
        .distinct()
    )

    asignacion_enfermero__jornada__turno = django_filters.ChoiceFilter(
        field_name='asignacion_enfermero__jornada__turno',
        label='Turno',
        empty_label='-- Sin filtros --',
        choices=[
            (t, Jorna_laboral.TURNOS_CHOICES_DICT[t]) 
            for t in unique_turnos
        ]
    )    
    
    fecha_y_horario = django_filters.DateFilter(
        method='filtrar_por_fecha',
        label='Fecha de subida:',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = ObservacionesEnfermero
        fields = [
            'asignacion_enfermero__enfermero__persona__first_name',
            'asignacion_enfermero__enfermero__persona__last_name',
            'asignacion_enfermero__enfermero__numero_matricula',
            'asignacion_enfermero__jornada__turno',
            'fecha_y_horario'
        ]
        
    def filtrar_por_fecha(self, queryset, name, value):  # Agregamos este metodo porque Django trata los campos con auto_now_add como: solo de creación, no editables y no filtrables directamente a menos que lo fuerces. Por eso este metodo resuelve el problema
        if value:
            inicio = datetime.combine(value, time.min)
            fin = datetime.combine(value, time.max)
            return queryset.filter(fecha_y_horario__range=(inicio, fin))
        return queryset     

class EnfermerosDeLaUnidadFilter(django_filters.FilterSet):
    usuario__numero_matricula = django_filters.CharFilter(
        field_name='usuario__numero_matricula',
        lookup_expr='icontains',
        label='Matricula enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por N° Matricula...'})
    )
    usuario__persona__first_name = django_filters.CharFilter(
        field_name='usuario__persona__first_name',
        lookup_expr='icontains',
        label='Nombre enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    usuario__persona__last_name = django_filters.CharFilter(
        field_name='usuario__persona__last_name',
        lookup_expr='icontains',
        label='Apellido enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    unique_turnos = (
        Jorna_laboral.objects
        .values_list("turno", flat=True)
        .distinct()
    )

    jornada__turno = django_filters.ChoiceFilter(
        field_name='jornada__turno',
        label='Turno',
        empty_label='-- Sin filtros --',
        choices=[
            (t, Jorna_laboral.TURNOS_CHOICES_DICT[t]) 
            for t in unique_turnos
        ]
    )
    
    
    class Meta:
        model = UsuarioLugarTrabajoAsignado
        fields = [
            'usuario__persona__first_name',
            'usuario__persona__last_name',
            'usuario__numero_matricula',
            'jornada__turno'
        ]


class ObservacionesDeEnfermeroFilter(django_filters.FilterSet):
    asignacion_enfermero__asignacion_habitacion__paciente__persona__dni = django_filters.CharFilter(
        field_name='asignacion_enfermero__asignacion_habitacion__paciente__persona__dni',
        lookup_expr='icontains',
        label='Dni del paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por Dni...'})
    )
    asignacion_enfermero__asignacion_habitacion__paciente__persona__first_name = django_filters.CharFilter(
        field_name='asignacion_enfermero__asignacion_habitacion__paciente__persona__first_name',
        lookup_expr='icontains',
        label='Nombre paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    asignacion_enfermero__asignacion_habitacion__paciente__persona__last_name = django_filters.CharFilter(
        field_name='asignacion_enfermero__asignacion_habitacion__paciente__persona__last_name',
        lookup_expr='icontains',
        label='Apellido paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    asignacion_enfermero__asignacion_habitacion__lugar = django_filters.ModelChoiceFilter(
        queryset=Lugar.objects.filter(tipo="hab"),
        label='Ubicacion',
        empty_label='-- Sin filtros --',
    )

    unique_turnos = (
        Jorna_laboral.objects
        .values_list("turno", flat=True)
        .distinct()
    )

    asignacion_enfermero__jornada__turno = django_filters.ChoiceFilter(
        field_name='asignacion_enfermero__jornada__turno',
        label='Turno',
        empty_label='-- Sin filtros --',
        choices=[
            (t, Jorna_laboral.TURNOS_CHOICES_DICT[t]) 
            for t in unique_turnos
        ]
    )    
    fecha_y_horario = django_filters.DateFilter(
        method='filtrar_por_fecha',
        label='Fecha de subida:',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = ObservacionesEnfermero
        fields = [
            'asignacion_enfermero__asignacion_habitacion__paciente__persona__dni',
            'asignacion_enfermero__asignacion_habitacion__paciente__persona__first_name',
            'asignacion_enfermero__asignacion_habitacion__paciente__persona__last_name',
            'asignacion_enfermero__jornada__turno',
            'fecha_y_horario'
        ]
        
    def filtrar_por_fecha(self, queryset, name, value):  # Agregamos este metodo porque Django trata los campos con auto_now_add como: solo de creación, no editables y no filtrables directamente a menos que lo fuerces. Por eso este metodo resuelve el problema
        if value:
            inicio = datetime.combine(value, time.min)
            fin = datetime.combine(value, time.max)
            return queryset.filter(fecha_y_horario__range=(inicio, fin))
        return queryset            


class EnfermerosDeLaUnidadFilter(django_filters.FilterSet):
    usuario__numero_matricula = django_filters.CharFilter(
        field_name='usuario__numero_matricula',
        lookup_expr='icontains',
        label='Matricula Enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por N° Matricula...'})
    )
    usuario__persona__first_name = django_filters.CharFilter(
        field_name='usuario__persona__first_name',
        lookup_expr='icontains',
        label='Nombre Enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    usuario__persona__last_name = django_filters.CharFilter(
        field_name='usuario__persona__last_name',
        lookup_expr='icontains',
        label='Apellido Enfermero:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    unique_turnos = (
        Jorna_laboral.objects
        .values_list("turno", flat=True)
        .distinct()
    )

    jornada__turno = django_filters.ChoiceFilter(
        field_name='jornada__turno',
        label='Turno',
        empty_label='-- Sin filtros --',
        choices=[
            (t, Jorna_laboral.TURNOS_CHOICES_DICT[t]) 
            for t in unique_turnos
        ]
    )
    
    
    class Meta:
        model = UsuarioLugarTrabajoAsignado
        fields = [
            'usuario__persona__first_name',
            'usuario__persona__last_name',
            'usuario__numero_matricula',
            'jornada__turno'
        ]

class EvaluacionesDelMedicoFilter(django_filters.FilterSet):
    asignacion_medico__asignacion_habitacion__paciente__persona__dni = django_filters.CharFilter(
        field_name='asignacion_medico__asignacion_habitacion__paciente__persona__dni',
        lookup_expr='icontains',
        label='Dni del paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por Dni...'})
    )
    asignacion_medico__asignacion_habitacion__paciente__persona__first_name = django_filters.CharFilter(
        field_name='asignacion_medico__asignacion_habitacion__paciente__persona__first_name',
        lookup_expr='icontains',
        label='Nombre paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    asignacion_medico__asignacion_habitacion__paciente__persona__last_name = django_filters.CharFilter(
        field_name='asignacion_medico__asignacion_habitacion__paciente__persona__last_name',
        lookup_expr='icontains',
        label='Apellido paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    asignacion_medico__asignacion_habitacion__lugar = django_filters.ModelChoiceFilter(
        queryset=Lugar.objects.filter(tipo="hab"),
        label='Ubicacion',
        empty_label='-- Sin filtros --',
    )   
    fecha_y_horario = django_filters.DateFilter(
        method='filtrar_por_fecha',
        label='Fecha de subida:',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = ObservacionesMedico
        fields = [
            'asignacion_medico__asignacion_habitacion__paciente__persona__dni',
            'asignacion_medico__asignacion_habitacion__paciente__persona__first_name',
            'asignacion_medico__asignacion_habitacion__paciente__persona__last_name',
            'fecha_y_horario'
        ]

    def filtrar_por_fecha(self, queryset, name, value):  # Agregamos este metodo porque Django trata los campos con auto_now_add como: solo de creación, no editables y no filtrables directamente a menos que lo fuerces. Por eso este metodo resuelve el problema
        if value:
            inicio = datetime.combine(value, time.min)
            fin = datetime.combine(value, time.max)
            return queryset.filter(fecha_y_horario__range=(inicio, fin))
        return queryset    

class MedicosConCitasFilter(django_filters.FilterSet):
    numero_matricula = django_filters.NumberFilter(
        field_name='numero_matricula',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='N° Matricula:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por el N° Matricula...'})
    )   
    persona__first_name = django_filters.CharFilter(
        field_name='persona__first_name',
        lookup_expr='icontains',
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    persona__last_name = django_filters.CharFilter(
        field_name='persona__last_name',
        lookup_expr='icontains',
        label='Apellido:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    rol_profesional = django_filters.ModelChoiceFilter(
        queryset=RolesProfesionales.objects.all(),
        field_name='UsuariosAsignadosAEsteLugar__rolProfesionalAsignado__rol_profesional',
        label='Especialidad',
        empty_label='-- Sin filtros ---'
    )
    
    todos_medicos = django_filters.BooleanFilter(
        method='filtrar_todos_medicos',
        label='Mostrar todos los médicos de mi turno',
        widget=forms.CheckboxInput()
    )


    
    class Meta:
        model = Usuario
        fields = [
            'numero_matricula',  
            'persona__first_name', 
            'persona__last_name',
            "rol_profesional",
            "todos_medicos"
        ]

    def __init__(self, *args, **kwargs):
        self.jornada = kwargs.pop('jornada', None)
        super().__init__(*args, **kwargs)

    def filtrar_todos_medicos(self, queryset, name, value):
        """
        Checkbox marcado: todos los médicos activos
        Checkbox desmarcado: solo médicos con cita en la jornada actual
        """
        hoy = timezone.localtime().date()

        if value:
            return queryset   # Mostrar todos los médicos activos (los filtros de nombre, apellido, especialidad y matrícula siguen aplicando)
        else:
            if self.jornada: # Solo médicos con cita hoy y en la jornada asignada
                return queryset.filter(turnosDelMedico__fecha_turno=hoy,UsuariosAsignadosAEsteLugar__jornada=self.jornada)
            else:            
                return queryset.filter(turnosDelMedico__fecha_turno=hoy)  # Si no hay jornada definida, filtramos solo por fecha de turno

    @property
    def qs(self):
        return super().qs.distinct()

class MedicosFilter(django_filters.FilterSet):
    numero_matricula = django_filters.NumberFilter(
        field_name='numero_matricula',
        lookup_expr='icontains',  # icontains:  buscar texto parcial  .  # exact : opción exacta
        label='N° Matricula:',
        widget=forms.NumberInput(attrs={'placeholder': 'Buscar por el N° Matricula...'})
    )   
    persona__first_name = django_filters.CharFilter(
        field_name='persona__first_name',
        lookup_expr='icontains',
        label='Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    persona__last_name = django_filters.CharFilter(
        field_name='persona__last_name',
        lookup_expr='icontains',
        label='Apellido:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    )
    
    class Meta:
        model = Usuario
        fields = [
            'numero_matricula',  
            'persona__first_name', 
            'persona__last_name',
        ]


class ConsultasDelMedicoFilter(django_filters.FilterSet):
    turno__paciente__persona__dni = django_filters.CharFilter(
        field_name='turno__paciente__persona__dni',
        lookup_expr='icontains',
        label='Dni del paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por Dni...'})
    )
    turno__paciente__persona__first_name = django_filters.CharFilter(
        field_name='turno__paciente__persona__first_name',
        lookup_expr='icontains',
        label='Nombre paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el nombre...'})
    )
    turno__paciente__persona__last_name = django_filters.CharFilter(
        field_name='turno__paciente__persona__last_name',
        lookup_expr='icontains',
        label='Apellido paciente:',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por el apellido...'})
    ) 
    fecha = django_filters.DateFilter(
        method='filtrar_por_fecha',
        label='Fecha:',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Consultas
        fields = [
            'turno__paciente__persona__dni',
            'turno__paciente__persona__first_name',
            'turno__paciente__persona__last_name',
            'fecha'
        ]
        
    def filtrar_por_fecha(self, queryset, name, value):  # Agregamos este metodo porque Django trata los campos con auto_now_add como: solo de creación, no editables y no filtrables directamente a menos que lo fuerces. Por eso este metodo resuelve el problema
        if value:
            inicio = datetime.combine(value, time.min)
            fin = datetime.combine(value, time.max)
            return queryset.filter(fecha__range=(inicio, fin))
        return queryset

