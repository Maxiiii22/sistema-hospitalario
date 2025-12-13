import datetime
from django.shortcuts import get_object_or_404
from hospital_personal.models import Especialidades,UsuarioLugarTrabajoAsignado,Turno,TurnoEstudio,ServicioDiagnostico


def obtener_disponibilidad(profesional_id, horario,especialidad_id,paciente_id):
    hoy = datetime.date.today()
    dias_disponibles = []
    
    dias_en_espanol = {
        "monday": "lunes",
        "tuesday": "martes",
        "wednesday": "miercoles",
        "thursday": "jueves",
        "friday": "viernes",
        "saturday": "sabado",
        "sunday": "domingo"
    }
    
    #Obtener las jornadas laborales del profesional 
    jornadas = UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=profesional_id,rolProfesionalAsignado__rol_profesional__especialidad__id=especialidad_id,estado="asignado")
    especialidad = get_object_or_404(Especialidades, pk=especialidad_id)
    limite = especialidad.capacidad_diaria
    
    # Iterar sobre los próximos 60 días
    for i in range(1, 61):  # Ver los próximos 60 días
        dia = hoy + datetime.timedelta(days=i) # Obtengo la fecha
        dia_semana_ingles = dia.strftime("%A").lower()  # Obtengo el nombre del dia segun la fecha
        dia_semana = dias_en_espanol.get(dia_semana_ingles, "") # Convertir el nombre del día en inglés a español
        
        # Verificar si el profesional trabaja en este día
        for jornada in jornadas:
            if jornada.jornada.dia == dia_semana and jornada.jornada.turno == horario:  # Si el profesional trabaja en este día y horario
                if not Turno.objects.filter(fecha_turno=dia, paciente_id=paciente_id,especialidad=especialidad,horario_turno=horario).exists():
                    if Turno.objects.filter(fecha_turno=dia,especialidad=especialidad,profesional=profesional_id,lugar=jornada.lugar).count() < limite:  # Si hay menos de limite de capacidad de cupos diarios entonces lo agregamos a las fechas disponibles
                        dias_disponibles.append({
                            "fecha": dia
                        })
                        break  # Ya encontramos que el profesional trabaja este día, no es necesario seguir buscando en las demás jornadas
            
    # Convertimos los días disponibles en un formato que pueda ser serializado a JSON
    dias_serializados = []
    for dia in dias_disponibles:
        dias_serializados.append({
            "fecha": dia["fecha"].strftime("%Y-%m-%d"),  # Formato de fecha serializable
        })

    return dias_serializados


def obtener_dias_disponibles_servicio(servicio_id,paciente_id,estudio_id):
    hoy = datetime.date.today()
    dias_disponibles = []
    servicio_diagnostico = get_object_or_404(ServicioDiagnostico, pk=servicio_id)
    limite = servicio_diagnostico.capacidad_diaria
    lugaresDisponibles = servicio_diagnostico.lugar.filter(activo=True)
    lugarDisponible = None
    for lugar in lugaresDisponibles:
        if TurnoEstudio.objects.filter(servicio_diagnostico=servicio_diagnostico,lugar=lugar).count() < limite:
            lugarDisponible = lugar
            break
        
    for i in range(1, 31):  # Desde mañana hasta 30 días después
        dia = hoy + datetime.timedelta(days=i)
        if dia.weekday() < 5: 
            if lugarDisponible is not None:
                if TurnoEstudio.objects.filter(fecha_turno=dia,servicio_diagnostico=servicio_diagnostico,lugar=lugarDisponible).count() < limite:  # Si hay menos de limite de capacidad de cupos diarios entonces lo agregamos a las fechas disponibles
                    if not TurnoEstudio.objects.filter(fecha_turno=dia, orden__paciente_id=paciente_id,orden__tipo_estudio_id=estudio_id).exists():                    
                        dias_disponibles.append({
                            "fecha": dia
                        })
    
    # Convertimos los días disponibles en un formato que pueda ser serializado a JSON
    dias_serializados = []
    for dia in dias_disponibles:
        dias_serializados.append({
            "fecha": dia["fecha"].strftime("%Y-%m-%d"),  # Formato de fecha serializable
        })

    return dias_serializados, lugarDisponible
