
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import personal_required # En controlUsuario.decorators creamos decoradores personalizados que verifiquen si el usuario tiene el atributo de paciente o usuario, y redirigirlo a una página de acceso denegado si intenta acceder a una vista que no le corresponde.
from controlUsuario.forms import FormularioActualizarPassword
from django.contrib.auth import update_session_auth_hash
from controlUsuario.models import Usuario
from hospital_pacientes.models import Paciente
from hospital_personal.models import Especialidades,EstudiosDiagnosticos,Departamento,Lugar,Turno,AsignacionEnfermero,ResultadoEstudio,UsuarioRolProfesionalAsignado,TurnoEstudio,SolicitudReactivacion,AsignacionesHabitaciones,UsuarioLugarTrabajoAsignado,AsignacionMedico
from django.utils import timezone
from django.db.models import Min
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

@personal_required
@login_required
def newPassword(request):
    persona = request.user 

    if request.method == "POST":
        form = FormularioActualizarPassword(request.POST, instance=persona)
        if form.is_valid():
            persona = form.save(commit=False)
            persona.usuario.debe_cambiar_contraseña = False 
            persona.usuario.save()
            persona.save() 
            update_session_auth_hash(request, persona) # Evita que se cierre la sesión
            return redirect("indexPersonal")
    else:
        form = FormularioActualizarPassword(instance=persona)

    return render(request, "newPassword.html", {"form": form})


@personal_required
@login_required
def indexPersonal(request):
    hoy = timezone.localtime().date() 
    usuario = request.user.usuario
    tipo_usuario = usuario.tipoUsuario.id        
    
    if tipo_usuario != 1:
        if usuario.debe_cambiar_contraseña:
            return redirect("newPassword")
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_especialidad = request.GET.get('id')
        # Verifica que la especialidad realmente pertenece al usuario
        if request.user.is_authenticated and hasattr(request.user, 'usuario'):
            if request.user.usuario.rolesProfesionalesUsuario.filter(rol_profesional__especialidad__id=id_especialidad).exists():
                request.session['especialidad_actual'] = id_especialidad
    
    if tipo_usuario == 1:
        usuarios_activos = Usuario.objects.filter(persona__is_active=True).count()
        pacientes = Paciente.objects.filter(persona__is_active=True).count()
        especialidades = Especialidades.objects.all().count()
        departamentos = Departamento.objects.all().count()
        estudios = EstudiosDiagnosticos.objects.all().count()
        lugares = Lugar.objects.filter(activo=True).count()
        
        context = {
            "usuarios_activos": usuarios_activos,
            "pacientes": pacientes,
            "especialidades": especialidades,
            "departamentos": departamentos,
            "estudios": estudios,
            "lugares": lugares,
        }
    elif tipo_usuario == 2:
        usuarios_activos = Usuario.objects.filter(persona__is_active=True).count()
        medicos = Usuario.objects.filter(persona__is_active=True,tipoUsuario_id=2).count()        
        turnos_hoy = Turno.objects.filter(fecha_turno=hoy).count()   
        turnos_futuros = Turno.objects.filter(fecha_turno__gt=hoy).count()   
        solicitudes_completadas = SolicitudReactivacion.objects.exclude(estado="pendiente").count()
        solicitudes_pendientes = SolicitudReactivacion.objects.filter(estado="pendiente").count()
        
        context = {
            "usuarios_activos": usuarios_activos,
            "medicos": medicos,
            "turnos_hoy": turnos_hoy,
            "turnos_futuros": turnos_futuros,
            "solicitudes_completadas": solicitudes_completadas,
            "solicitudes_pendientes": solicitudes_pendientes,
        }
    elif tipo_usuario == 3:
        rolesDelMedico = usuario.rolesProfesionalesUsuario.all()

        especialidades = [rol.rol_profesional.especialidad for rol in rolesDelMedico]         
        
        turnos_especialidad = []

        for especialidad in especialidades:
            cant = Turno.objects.filter(
                fecha_turno=hoy,
                especialidad=especialidad,
                profesional=usuario
            ).count()   

            cantFuturos = Turno.objects.filter(
                fecha_turno__gt=hoy,
                especialidad=especialidad,
                profesional=usuario
            ).count()   

            turnos_especialidad.append({
                "especialidad": especialidad.nombre_especialidad,
                "cant": cant,
                "cantFuturos": cantFuturos
            })
                
        context = {
            "turnos_especialidad": turnos_especialidad
        }
    elif tipo_usuario == 4:
        pacientesACargo = AsignacionEnfermero.objects.filter(enfermero=usuario,activo=True).count()
        
        context = {
            "pacientesACargo": pacientesACargo,
        }        
    elif tipo_usuario == 6:
        rolesDelUsuario = UsuarioRolProfesionalAsignado.objects.filter(usuario=request.user.usuario)

        mapa_roles = {
            81: "lab",
            82: "img",
            83: "fisio",
            84: "eval"
        }

        mapa_contexto = {
            "lab": "Estudios de laboratorio pendientes de carga",
            "img": "Estudios de imagen pendientes de carga",
            "fisio": "Estudios fisiológicos pendientes de carga",
            "eval": "Estudios de evaluación pendientes de carga"
        }

        tipoResultados = [
            mapa_roles[rol.rol_profesional.id]
            for rol in rolesDelUsuario
            if rol.rol_profesional.id in mapa_roles
        ]

        estudiosPendientesDeCarga = TurnoEstudio.objects.filter(estado="analisis").count()

        estudiosUsuario = []

        for rol in tipoResultados:
            estudiosUsuario.append({
                "titulo": mapa_contexto[rol],
                "cantidad": TurnoEstudio.objects.filter(
                    estado="analisis",
                    orden__tipo_estudio__tipo_resultado=rol
                ).count()
            })

        context = {
            "estudiosPendientesDeCarga": estudiosPendientesDeCarga,
            "estudiosUsuario": estudiosUsuario,
        }        
    
    elif tipo_usuario == 7:
        pacientes = Paciente.objects.filter(persona__is_active=True).count()
        pacientesHospitalizados = AsignacionesHabitaciones.objects.filter(estado="activa").count()
        asignacionTrabajo = request.user.usuario.get_asignacionActual()
        unidad = asignacionTrabajo.get("idLugarAsignacion")
        try:
            lugar = Lugar.objects.get(pk=unidad)
        except ObjectDoesNotExist:
            response = render(request, "403.html", {
                "mensaje": "No puedes acceder al sistema ya que no tienes ninguna asignacion hoy."
            })
            response.status_code = 403
            return response   

        if unidad is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
            enfermerosDeLaUnidad = UsuarioLugarTrabajoAsignado.objects.filter(lugar=lugar.unidad,usuario__tipoUsuario_id=4,usuario__persona__is_active=True).values('usuario_id').annotate(id_min=Min('id')).count()  
            
            medicosDeLaUnidad = (
                UsuarioLugarTrabajoAsignado.objects.filter(lugar=lugar.unidad,usuario__tipoUsuario_id=8,usuario__persona__is_active=True).values('usuario_id').annotate(id_min=Min('id')).count()  
            )
        else:
            enfermerosDeLaUnidad = 0
            medicosDeLaUnidad = 0
            
        habitaciones = Lugar.objects.filter(tipo="hab",activo=True,unidad=lugar.unidad).count()
        
        habitacionesDisponibles=0
        for habitacion in Lugar.objects.filter(tipo="hab",activo=True,unidad=lugar.unidad):
            capacidadMax = habitacion.capacidad
            if not AsignacionesHabitaciones.objects.filter(lugar=habitacion,estado="activa").count() >= capacidadMax:
                habitacionesDisponibles += 1
        
        context = {
            "pacientes": pacientes,
            "pacientesHospitalizados": pacientesHospitalizados,
            "enfermerosDeLaUnidad": enfermerosDeLaUnidad,
            "medicosDeLaUnidad": medicosDeLaUnidad,
            "habitaciones": habitaciones,
            "habitacionesDisponibles": habitacionesDisponibles,
        }
    elif tipo_usuario == 8:
        pacienteAsignados = AsignacionMedico.objects.filter(medico=request.user.usuario,asignacion_habitacion__estado="activa").count()
        misAsignacionesDeHospitalizacion = AsignacionMedico.objects.filter( medico=request.user.usuario,asignacion_habitacion__estado="activa").values_list('asignacion_habitacion_id', flat=True)
        misEnfermerosACargo = AsignacionEnfermero.objects.filter(asignacion_habitacion__id__in=misAsignacionesDeHospitalizacion,asignacion_habitacion__estado="activa").values("enfermero_id").annotate(id_min=Min("id"))
        enfermeros_ids = misEnfermerosACargo.values_list("enfermero_id",flat=True)
        
        enfermerosDeLaUnidad = UsuarioLugarTrabajoAsignado.objects.filter(usuario__id__in=enfermeros_ids,usuario__tipoUsuario_id=4,usuario__persona__is_active=True).values('usuario_id').annotate(id_min=Min('id')).count()  
            
        
        context = {
            "pacienteAsignados": pacienteAsignados,
            "enfermerosDeLaUnidad": enfermerosDeLaUnidad,
        }
        
                
        
        
        
    return render(request, "indexPersonal.html",context) 