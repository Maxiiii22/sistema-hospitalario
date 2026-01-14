from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser 
from hospital_personal.models import Especialidades,ServicioDiagnostico,Departamento


# Create your models here.

##### Toda esta parte es para que todos los personas usen login_id en vez de username ######
class PersonaManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, login_id, password=None, **extra_fields):
        if not login_id:
            raise ValueError('El campo login_id es obligatorio')
        extra_fields.setdefault('is_active', True)
        user = self.model(login_id=login_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(login_id, password, **extra_fields)
    
#############################################################################################

class TiposUsuarios(models.Model): 
    nombre_tipoUsuario = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.nombre_tipoUsuario}"
    
class RolesProfesionales(models.Model):  
    nombre_rol_profesional = models.CharField(max_length=255)
    tipoUsuario = models.ForeignKey(TiposUsuarios,on_delete=models.PROTECT)
    especialidad = models.ForeignKey(Especialidades,on_delete=models.PROTECT, blank=True, null=True)
    servicio_diagnostico = models.ForeignKey(ServicioDiagnostico,on_delete=models.PROTECT, blank=True, null=True)
    departamento = models.ForeignKey(Departamento,on_delete=models.PROTECT, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre_rol_profesional}"
    
    def clean(self):
        if self.tipoUsuario.id in [3, 4, 8]: # Medico, Enfermero y Medico tratante
            if self.especialidad is None or self.servicio_diagnostico or self.departamento:
                raise ValidationError(f"Un {self.tipoUsuario.nombre_tipoUsuario} debe estar asignado a una especialidad exclusivamente.")
        elif self.tipoUsuario.id == 7: # Jefe de enfermeria
            if self.departamento is None or self.especialidad or self.servicio_diagnostico:
                raise ValidationError(f"Un {self.tipoUsuario.nombre_tipoUsuario} debe estar asignado a un departamento exclusivamente.")
        elif self.tipoUsuario.id == 5: # Apoyo en Diagnóstico y Tratamiento
            if self.servicio_diagnostico is None or self.especialidad or self.departamento:
                raise ValidationError(f'Un usuario de "{self.tipoUsuario.nombre_tipoUsuario}" debe estar asignado a un servicio de diagnóstico exclusivamente.')
        else:
            if self.especialidad or self.servicio_diagnostico or self.departamento:
                raise ValidationError(f"Un {self.tipoUsuario.nombre_tipoUsuario} no puede estar asignado a una especialidad, a un servicio de diagnóstico o un departamento.")
    
    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)


class Persona(AbstractUser): 
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino')
    ]    
    
    username = None   # Eliminamos username porque usamos login_id en su lugar
    dni = models.CharField(max_length=8, unique=True)
    login_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # login_id guardara tanto los emails de los pacientes , como el legajo_hospitalario de los usuarios.
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    telefono = models.CharField(max_length=20, blank=True, null=True,unique=True)
    

    USERNAME_FIELD = 'login_id'  # Esto le dice a Django qué campo usar para autenticar usuarios (es decir, con qué campo hacen login).
    REQUIRED_FIELDS = ['first_name', 'last_name',"fecha_nacimiento"]  # A REQUIRED_FIELDS Django lo usa cuando creás superusuarios. Se refiere a los campos que pedirá además de login_id y password.

    objects = PersonaManager()  # Usamos el manager personalizado

    def __str__(self):
        if self.login_id:
            return f"{self.get_full_name()} ({self.login_id}) - DNI: {self.dni}"
        else:
            return f"{self.get_full_name()} (Menor a cargo del DNI: {self.paciente.responsable.adulto.persona.dni})"
    
    class Meta: 
        verbose_name = "Persona"  # Esto hace que en el admin diga "Personas" en lugar de "Users".
        verbose_name_plural = "Personas"


class Usuario(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.PROTECT)
    numero_matricula = models.CharField(max_length=50, blank=True, null=True)
    debe_cambiar_contraseña = models.BooleanField(default=True)
    tipoUsuario = models.ForeignKey(TiposUsuarios, on_delete=models.PROTECT)
    
    
    # Queremos que los valores NO vacíos sean únicos, pero permitir múltiples registros vacíos o nulos.
    # No usamos solamente `unique=True` en numero_matricula porque:
    #   - Django trata "" como un valor real, y eso rompería la unicidad si hay más de un "".
    #   - Algunas bases de datos (como SQLite o MySQL) no permiten múltiples NULL con unique=True.
    # Por eso, validamos manualmente en `clean()` cuando el valor no está vacío.        
    def clean(self):
        super().clean()  
        if self.numero_matricula:
            qs = Usuario.objects.filter(numero_matricula=self.numero_matricula)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'numero_matricula': "Este número de matrícula ya está en uso."})
    
    def tipoUsuario_display(self):
        """
        Devuelve el nombre del rol adaptado al sexo del usuario.
        """
        EXCEPCIONES_FEMENINAS = {
            "Superadministrador": "Superadministradora",
            "Administrador": "Administradora",
            "Enfermero": "Enfermera",
            "Jefe de Enfermería": "Jefa de Enfermería",
        }        
        
        nombre = self.tipoUsuario.nombre_tipoUsuario

        if getattr(self.persona, 'sexo', 'M') != 'F':
            return nombre  

        # Primero revisar excepciones
        if nombre in EXCEPCIONES_FEMENINAS:
            return EXCEPCIONES_FEMENINAS[nombre]

        # Separar palabras
        palabras = nombre.split(" ")
        resultado = []

        for palabra in palabras:
            if palabra.endswith("o"):  # Médico → Médica
                resultado.append(palabra[:-1] + "a")
            elif palabra.endswith("or"):  # Operador → Operadora
                resultado.append(palabra + "a")
            else:
                resultado.append(palabra)  # No cambia

        return " ".join(resultado)
    
    def get_rolesProfesionales(self):
        roles = self.rolesProfesionalesUsuario.select_related('rol_profesional').all()
        nombres_roles = [r.rol_profesional.nombre_rol_profesional for r in roles]
        return ", ".join(nombres_roles)
    
    def get_asignacionActual(self):
        ahora = timezone.localtime()
        hora_actual = ahora.time()        
        hoy = ahora.date()
        nombre_dia = hoy.strftime('%A').lower()
        
        dias_en_espanol = {
            "monday": "lunes",
            "tuesday": "martes",
            "wednesday": "miercoles",
            "thursday": "jueves",
            "friday": "viernes",
            "saturday": "sabado",
            "sunday": "domingo"
        }
        

        dia_semana = dias_en_espanol.get(nombre_dia, "") # Convertir el nombre del día en inglés a español
        asignacionTrabajo = self.UsuariosAsignadosAEsteLugar.all()
        if not asignacionTrabajo:
            return {
                "asignacion": False,
                "dia_no_laborable": False,
                "dentro_del_turno": False,
                "rango": None,
                "idJornadaAsignada": None,                
                "asignacionActualId": None,              
                "asignacionActual": None,
                "idLugarAsignacion": None,              
                "NombreLugarAsignacion": None              
            }           
        
        for asignacion in asignacionTrabajo:
            if asignacion.jornada.dia == dia_semana:
                horaInicio,horaFinal = asignacion.jornada.obtener_rango_turno()
                dentro_del_turno = horaInicio <= hora_actual <= horaFinal
                return {
                    "asignacion": True,
                    "dia_no_laborable": True,                    
                    "dentro_del_turno": dentro_del_turno,
                    "rango": (horaInicio, horaFinal),
                    "idJornadaAsignada": asignacion.jornada.id,
                    "asignacionActualId": asignacion.rolProfesionalAsignado.rol_profesional.id,
                    "asignacionActual": asignacion.rolProfesionalAsignado.rol_profesional.nombre_rol_profesional,
                    "idLugarAsignacion": asignacion.lugar.id,
                    "NombreLugarAsignacion": asignacion.lugar.nombre                     
                    
                }
        
        return {
                "asignacion": True,
                "dia_no_laborable": False,                                    
                "dentro_del_turno": False,
                "rango": None,
                "idJornadaAsignada": None,                                
                "asignacionActualId": None,  
                "asignacionActual": None,
                "idLugarAsignacion": None,  
                "NombreLugarAsignacion": None              
        }        
                
    
    
    def __str__(self):
        return f"Usuario: {self.id} - {self.persona.get_full_name()} - Legajo hospitalario: {self.persona.login_id}"

