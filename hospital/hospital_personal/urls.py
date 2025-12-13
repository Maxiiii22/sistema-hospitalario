from django.urls import path
from .views import superadministrador_views, medico_views, general_views, operadorResultados_views, jefeEnfermeria_views, medicoHospitalario_views, enfermero_views, administrador_views

urlpatterns = [
    path("", general_views.indexPersonal, name="indexPersonal"),
    path("cambiar-password/", general_views.newPassword, name="newPassword"),
    # Superadministrador:
    path("superadmin/gestion-personal/", superadministrador_views.gestionDelPersonal, name="gestionDelPersonal"),
    path("superadmin/gestion-personal/alta-personal", superadministrador_views.altaPersonal, name="altaPersonal"),
    path("superadmin/detalles-usuario-<int:id>",superadministrador_views.detalle_usuario, name ="detalle_usuario"),
    path("superadmin/get-lugarTrabajoORolProfesional/",superadministrador_views.getLugarTrabajoORolProfesional, name ="getLugarTrabajoORolProfesional"), 
    path("superadmin/get-lugarTrabajoDisponibilidad/",superadministrador_views.getLugarTrabajoDisponibilidad, name ="getLugarTrabajoDisponibilidad"), 
    path("superadmin/delete-lugarTrabajo/<int:id_lugarTrabajo>",superadministrador_views.deleteLugarTrabajo, name ="deleteLugarTrabajo"), 
    path("superadmin/delete-rolProfesional/<int:id_rolProfesionalAsignado>",superadministrador_views.deleteRolProfesionalAsignado, name ="deleteRolProfesionalAsignado"), 
    path("superadmin/gestion-departamentos/", superadministrador_views.gestionDeDepartamentos, name="gestionDeDepartamentos"),
    path("superadmin/gestion-roles/", superadministrador_views.gestionDeRoles, name="gestionDeRoles"),
    path("superadmin/gestion-especialidades/", superadministrador_views.gestionDeEspecialidades, name="gestionDeEspecialidades"),
    path("superadmin/gestion-servicios-diagnosticos/", superadministrador_views.gestionDeServiciosDiagnostico, name="gestionDeServiciosDiagnostico"),
    path("superadmin/gestion-estudios-diagnosticos/", superadministrador_views.gestionDeEstudiosDiagnostico, name="gestionDeEstudiosDiagnostico"),
    path("superadmin/gestion-plantillas-estudios/", superadministrador_views.gestionDePlantillasEstudios, name="gestionDePlantillasEstudios"),
    path("superadmin/gestion-lugares/", superadministrador_views.gestionDeLugares, name="gestionDeLugares"),
    path("superadmin/lista-pacientes/", superadministrador_views.listaPacientes, name="listaPacientes"),
    path("superadmin/lista-pacientes/turnos-paciente-<int:id>", superadministrador_views.turnosPaciente, name="turnosPaciente"),
    # Administrador:
    path("administrador/gestion-personal/", administrador_views.gestionDelPersonal, name="administrador-gestionDelPersonal"),
    path("administrador/gestion-personal/detalles-usuario-<int:id_usuario>", administrador_views.detalle_usuario, name="administrador-detalle-usuario"),
    path("administrador/gestion-agendas/", administrador_views.gestionAgendas, name="administrador-gestion-agendas"),
    path("administrador/gestion-agendas/agenda-medico-<int:id_medico>/", administrador_views.agendaMedico, name="administrador-agenda-medico"),
    path("administrador/reportes/", administrador_views.reportes, name="administrador-reporte"),
    path('administrador/reportes/<int:anio>/<int:mes>/', administrador_views.reportes, name='administrador-reporte_mes'),    
    path('administrador/reportes/<int:anio>/<int:mes>/<int:dia>/', administrador_views.reportes, name='administrador-reporte_dia'), 
    path("administrador/reportes-servicios/", administrador_views.reportes_servicios, name="administrador-reporte-servicio"),
    path('administrador/reportes-servicios/<int:anio>/<int:mes>/', administrador_views.reportes_servicios, name='administrador-reporte-servicio_mes'),  
    path('administrador/reportes-servicios/<int:anio>/<int:mes>/<int:dia>/', administrador_views.reportes_servicios, name='administrador-reporte-servicio_dia'), 
    path("administrador/lista-medicos/", administrador_views.listaMedicos, name="administrador-lista-medicos"),
    path("administrador/productividad-medica-<int:id_medico>/", administrador_views.productividadMedica, name="administrador-productividad-medica"),
    path('administrador/productividad-medica-<int:id_medico>/<int:anio>/<int:mes>/', administrador_views.productividadMedica, name='administrador-productividad-medica_mes'),  
    path('administrador/productividad-medica-<int:id_medico>/<int:anio>/<int:mes>/<int:dia>/', administrador_views.productividadMedica, name='administrador-productividad-medica_dia'), 
    # # Medico de consultorio:
    path("medico-consultorio/turnos/", medico_views.turnosProgramados, name="turnosProgramados"),
    path("medico-consultorio/turnos/reprogramar/<int:turno_id>/", medico_views.reprogramarTurno, name="reprogramarTurno-medico"),
    path("medico-consultorio/turnos/cancelar/<int:turno_id>/", medico_views.cancelarTurno, name="cancelarTurno-medico"),
    path("medico-consultorio/consultas/", medico_views.historialConsultas, name="historialConsultas"),
    path("medico-consultorio/consultas/registrar/<int:id_turno>", medico_views.registrarConsulta, name="registrarConsulta"),
    path("medico-consultorio/consultas/editar/<int:id_consulta>", medico_views.editarConsulta, name="editarConsulta"),
    path("medico-consultorio/consultas/detalles/<int:id_consulta>", medico_views.detallesConsulta, name="detallesConsulta"),
    # Enfermeros:
    path("enfermero/pacientes/",enfermero_views.listaPacientes, name="pacientes-enfermero"),
    path("enfermero/pacientes/ficha-paciente/<int:id_asignacionHabitacion>",enfermero_views.fichaPaciente, name="fichaPaciente-enfermero"),    
    path("enfermero/pacientes/ficha-paciente/notas-enfermeria/<int:id_asignacionHabitacion>",enfermero_views.notasEnfermeria, name="notasEnfermeria-enfermero"),
    # Cargador de resultados:
    path("operador-resultados/estudios-disponibles/", operadorResultados_views.verEstudios, name="verEstudios"),
    path("operador-resultados/estudios-disponibles/cargar-resultados-turno-estudio-<int:turno_id>", operadorResultados_views.cargar_resultado, name="cargar_resultado"),
    #Jefe de enfermeria:
    path("jefe-enfermeria/pacientes/",jefeEnfermeria_views.listaPacientes, name="pacientes-jefe-enfermeria"),
    path("jefe-enfermeria/pacientes/ficha-paciente/<int:id_paciente>/",jefeEnfermeria_views.fichaPaciente, name="fichaPaciente"),
    path("jefe-enfermeria/pacientes/hospitalizaciones/<int:id_paciente>/",jefeEnfermeria_views.historialHospitalizacionPaciente, name="hospitalizacionesPaciente-jefe-enfermeria"),
    path("jefe-enfermeria/pacientes/ficha-hospitalizacion/<int:id_hospitalizacion>/",jefeEnfermeria_views.fichaHospitalizacion, name="fichaHospitalizacion-jefe-enfermeria"),
    path("jefe-enfermeria/pacientes/ficha-hospitalizacion/notas-enfermeria/<int:id_hospitalizacion>",jefeEnfermeria_views.notasEnfermeria, name="notasEnfermeria-jefe-enfermeria"),
    path('jefe-enfermeria/medico-tratante-autocomplete/', jefeEnfermeria_views.MedicoTratanteAutocomplete.as_view(), name='medico-tratante-autocomplete'),  # Para el autocomplete del FormAsignarMedicoTratante
    path('jefe-enfermeria/enfermero-autocomplete/', jefeEnfermeria_views.EnfermeroAutocomplete.as_view(), name='enfermero-autocomplete'),  # Para el autocomplete del FormAsignarEnfermero
    path("jefe-enfermeria/enfermeros/",jefeEnfermeria_views.enfermerosDeLaUnidad, name="enfermeros-jefe-enfermeria"),
    path("jefe-enfermeria/enfermeros/ficha-enfermero/<int:id_enfermero>",jefeEnfermeria_views.fichaEnfermero, name="fichaEnfermero-jefe-enfermeria"),
    path("jefe-enfermeria/enfermeros/ficha-enfermero/historial-notas-enfermero/<int:id_enfermero>/",jefeEnfermeria_views.historialNotasEnfermero, name="historialNotasEnfermero-jefe-enfermeria"),
    path("jefe-enfermeria/medicos/",jefeEnfermeria_views.medicosDeLaUnidad, name="medicos-jefe-enfermeria"),
    path("jefe-enfermeria/medicos/ficha-medico/<int:id_medico>",jefeEnfermeria_views.fichaMedico, name="fichaMedico-jefe-enfermeria"),
    path("jefe-enfermeria/medicos/ficha-medico/historial-evaluaciones-medicas/<int:id_medico>/",jefeEnfermeria_views.historialEvaluacionesMedicas, name="historialEvaluacionesMedicas-jefe-enfermeria"),
    # Medico hospitalario:
    path("medico-hospitalario/pacientes/",medicoHospitalario_views.listaPacientes, name="pacientes-medico-hospitalario"),
    path("medico-hospitalario/pacientes/ficha-paciente/<int:id_asignacionHabitacion>/",medicoHospitalario_views.fichaPaciente, name="fichaPaciente-medico-hospitalario"),
    path("medico-hospitalario/pacientes/ficha-paciente/notas-enfermeria/<int:id_asignacionHabitacion>",medicoHospitalario_views.notasEnfermeria, name="notasEnfermeria-medico-hospitalario"),
    path("medico-hospitalario/enfermeros/",medicoHospitalario_views.enfermerosDeLaUnidad, name="enfermeros-medico-hospitalario"),
    path("medico-hospitalario/enfermeros/ficha-enfermero/<int:id_enfermero>",medicoHospitalario_views.fichaEnfermero, name="fichaEnfermero-medico-hospitalario"),
    path("medico-hospitalario/pacientes/ficha-paciente/notas-enfermeria/<int:id_asignacionHabitacion>",medicoHospitalario_views.notasEnfermeria, name="notasEnfermeria-medico-hospitalario"),
    path("medico-hospitalario/enfermeros/ficha-enfermero/historial-notas-enfermero/<int:id_enfermero>/",medicoHospitalario_views.historialNotasEnfermero, name="historialNotasEnfermero-medico-hospitalario"),
    
]   