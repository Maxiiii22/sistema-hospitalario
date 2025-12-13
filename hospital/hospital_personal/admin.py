from django.contrib import admin

from .models import Especialidades,Departamento,Jorna_laboral,UsuarioLugarTrabajoAsignado,UsuarioRolProfesionalAsignado,Turno,Consultas,Medicaciones,OrdenEstudio,TurnoEstudio,ResultadoEstudio,EstudiosDiagnosticos,Lugar,ServicioDiagnostico,PlantillaEstudio,AsignacionesHabitaciones,AsignacionEnfermero,ObservacionesEnfermero,AsignacionMedico,ObservacionesMedico,AltaMedica,AltaAdministrativa

# Register your models here.

class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_departamento','tipo']

class EspecialidadesAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_especialidad','permite_turno','departamento',"capacidad_diaria"]

class Jornada_laboralAdmin(admin.ModelAdmin):
    list_display = ['id', 'dia','turno']

class LugarAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre','tipo','piso','sala','abreviacion','capacidad','es_critico','activo',"departamento"]

class MedicacionesAdmin(admin.ModelAdmin):
    list_display = ['id', 'medicamento','dosis','frecuencia','tiempo_uso','consulta','recetada_por']

class ServicioDiagnosticoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_servicio','departamento',"capacidad_diaria"]

class TurnoAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha_creacion','fecha_turno','horario_turno','estado','asistio','especialidad',"lugar",'paciente','profesional']

class TurnoEstudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha_creacion','fecha_turno','horario_turno','estado','orden','servicio_diagnostico','lugar','asistio']

class UsuarioRolProfesionalAsignadoAdmin(admin.ModelAdmin):
    list_display = ['id','rol_profesional','usuario']

admin.site.register(Especialidades,EspecialidadesAdmin)
admin.site.register(Departamento,DepartamentoAdmin)
admin.site.register(Jorna_laboral,Jornada_laboralAdmin)
admin.site.register(UsuarioLugarTrabajoAsignado)
admin.site.register(UsuarioRolProfesionalAsignado,UsuarioRolProfesionalAsignadoAdmin)
admin.site.register(Turno,TurnoAdmin)
admin.site.register(Lugar,LugarAdmin)
admin.site.register(Consultas)
admin.site.register(Medicaciones,MedicacionesAdmin)
admin.site.register(EstudiosDiagnosticos)
admin.site.register(OrdenEstudio)
admin.site.register(TurnoEstudio,TurnoEstudioAdmin)
admin.site.register(ResultadoEstudio)
admin.site.register(ServicioDiagnostico,ServicioDiagnosticoAdmin)
admin.site.register(PlantillaEstudio)
admin.site.register(AsignacionesHabitaciones)
admin.site.register(AsignacionEnfermero)
admin.site.register(ObservacionesEnfermero)
admin.site.register(AsignacionMedico)
admin.site.register(ObservacionesMedico)
admin.site.register(AltaMedica)
admin.site.register(AltaAdministrativa)

