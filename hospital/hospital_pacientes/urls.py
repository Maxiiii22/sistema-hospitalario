from django.urls import path
from . import views 

urlpatterns = [
    path("", views.indexPaciente, name="indexPaciente"),
    path("error403/", views.mi_error_403, name="mi_error_403"),
    # path('probar-error/', views.probar_404, name="error_404"),
    path("mi-cuenta/", views.miCuenta, name="miCuenta"),
    path("mi-cuenta/nueva-contraseña/", views.nuevaContraPaciente, name="nuevaContraPaciente"),
    path("turnos/ver-turnos/", views.misTurnos, name="misTurnos"),
    path("turnos/ver-turnos/<int:id_paciente>/", views.susTurnos, name="susTurnos"),
    path("turnos/solicitar/<int:paciente_id>", views.seleccionarTurno, name="seleccionarTurno"),
    path("turnos/solicitar-consulta/<int:paciente_id>/", views.sacarTurno, name="sacarTurno"),
    path("turnos/solicitar-estudio/<int:paciente_id>/", views.sacarTurnoEstudio, name="sacarTurnoEstudio"),
    path("turnos/turno-confirmado/<int:turno_id>/", views.turno_confirmado, name="turnoConfirmado"),
    path("turnos/estudio-confirmado/<int:turno_id>/", views.turno_estudio_confirmado, name="turnoEstudioConfirmado"),
    path("turnos/reprogramar/<int:turno_id>/", views.reprogramarTurno, name="reprogramarTurno-paciente"),
    path("turnos/reprogramar-estudio/<int:turno_id>/", views.reprogramarTurnoEstudio, name="reprogramarTurnoEstudio-paciente"),
    path("turnos/cancelar/<int:turno_id>/", views.cancelarTurno, name="cancelarTurno-paciente"),
    path("turnos/cancelar-estudio/<int:turno_id>/", views.cancelarTurnoEstudio, name="cancelarTurnoEstudio-paciente"),
    path("historial/", views.miHistorial, name="miHistorial"),
    path("historial/<int:id_paciente>", views.suHistorial, name="suHistorial"),
    path("turnos/consultas/consulta-turno-<int:id_turno>", views.consultaEspecifica, name="consultaEspecifica"),
    path("turnos/estudios/estudio-turno-<int:id_turno>", views.resultadoEstudioEspecifico, name="resultadoEstudioEspecifico"),
    path("registro-menor/", views.registrarMenor, name="registrarMenor"),
    path("gestion-menor/", views.gestionMenores, name="gestionMenores")
]