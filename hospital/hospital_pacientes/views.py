from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import paciente_required  # En controlUsuario.decorators creamos decoradores personalizados que verifiquen si el usuario tiene el atributo de paciente o usuario, y redirigirlo a una página de acceso denegado si intenta acceder a una vista que no le corresponde.
from hospital_personal.models import Especialidades,UsuarioRolProfesionalAsignado,UsuarioLugarTrabajoAsignado,Turno,Consultas,Medicaciones,OrdenEstudio,Jorna_laboral,TurnoEstudio,Lugar,ResultadoEstudio
from hospital_personal.forms import FormSacarTurno,FormSacarTurnoEstudio
from controlUsuario.models import Usuario,Persona
from controlUsuario.forms import FormularioRegistroPersonalizado
from .utils import obtener_disponibilidad, obtener_dias_disponibles_servicio
from .models import Paciente,MenorACargoDePaciente
from .forms import RegistrarMenorForm
from .filters import ConsultasFilter
from django.urls import reverse
from django.utils import timezone
from django.db.models import Min
from django.contrib import messages
from django.db import transaction
from datetime import datetime

# Create your views here.

def mi_error_403(request, exception=None):
    return render(request, "403.html", status=403)

# def probar_404(request):
#     return render(request, "404.html", status=404)

@paciente_required
@login_required
def indexPaciente(request):
    turnos = Turno.objects.filter(paciente=request.user.paciente,estado="pendiente").count()
    turnosEstudio = TurnoEstudio.objects.filter(orden__paciente=request.user.paciente,estado="pendiente").count()
    menores = request.user.paciente.menores_a_cargo.values("menor")
    turnosMenoresACargo = Turno.objects.filter(paciente__in=menores,estado="pendiente").count()
    turnosEstudioMenoresACargo = TurnoEstudio.objects.filter(orden__paciente__in=menores,estado="pendiente").count()

    context = {
        "turnos": turnos,
        "turnosEstudio": turnosEstudio,
        "turnosMenoresACargo": turnosMenoresACargo if turnosMenoresACargo else None,
        "turnosEstudioMenoresACargo": turnosEstudioMenoresACargo if turnosEstudioMenoresACargo else None,
    }    
    return render(request, "indexPacientes.html",context)

@paciente_required
@login_required
def miCuenta(request):
    persona_actual = request.user
    form = FormularioRegistroPersonalizado(instance=persona_actual)
    
    if request.method == "POST":   
        tipo_form = request.POST.get("tipo_form") 
        
        if tipo_form == "formMiCuenta":
            form = FormularioRegistroPersonalizado(request.POST, instance=persona_actual)
            if form.is_valid():
                form.save()
                return redirect("miCuenta") 
        
        elif tipo_form == "formCancelarPago":
            id_paciente_persona = request.POST.get("id_paciente_persona")

            if id_paciente_persona:
                try:
                    id_paciente_persona = int(id_paciente_persona)
                except (TypeError, ValueError):
                    id_paciente_persona = None
                    messages.error(request,"El campo tiene que ser un entero.")
                    return redirect("miCuenta")
            else:
                messages.error(request,"El campo no debe estar vacio.")
                return redirect("miCuenta")                       

            if id_paciente_persona is not None:
                persona = get_object_or_404(Persona, pk=id_paciente_persona)
                if persona_actual != persona:
                    response = render(request, "403.html", {
                        "mensaje": "No tienes acceso a esta persona."
                    })
                    response.status_code = 403
                    return response     
                    
                try:
                    with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                        for menor in persona_actual.paciente.menores_a_cargo.all():
                            Turno.objects.filter(paciente=menor.menor, estado="pendiente").update(estado="cancelado")
                            TurnoEstudio.objects.filter(orden__paciente=menor.menor, estado="pendiente").update(estado="cancelado")

                        Turno.objects.filter(paciente=persona_actual.paciente, estado="pendiente").update(estado="cancelado")
                        TurnoEstudio.objects.filter(orden__paciente=persona_actual.paciente, estado="pendiente").update(estado="cancelado")
                        Persona.objects.filter(paciente__responsable__adulto=persona_actual.paciente).update(is_active=False)                        
                        persona_actual.is_active = False
                        persona_actual.save()
                        messages.success(request, "Su servicio fue cancelado correctamente. Podrá reactivarlo cuando lo desee.")             
                        return redirect("logout")                       
                except Exception as e:
                    print(e)
                    messages.error(request, "No fue posible cancelar su cuota hospitalaria ni las cuotas correspondientes a los menores a su cargo. Por favor, intente nuevamente o comuníquese con administración.")             
                    return redirect("miCuenta")                  
        
    
    return render(request, "miCuenta.html", {"form":form}) 

@paciente_required
@login_required
def misTurnos(request):
    paciente_actual = request.user.paciente    
    
    if request.method == "GET" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        id_turno_medico = request.GET.get("id_turno_medico")
        id_turno_estudio = request.GET.get("id_turno_estudio")
        
        if id_turno_medico:
            if not Turno.objects.filter(pk=id_turno_medico,estado="pendiente").exists():
                response = render(request, "403.html", {
                    "mensaje": "Este turno no existe o ya fue atendidó."
                })
                response.status_code = 403
                return response    
            
            turno = get_object_or_404(Turno, id=id_turno_medico)
            
            # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
            if turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.paciente).exists():
                return HttpResponseForbidden(render(request, "403.html"))
            
            disponibilidad = obtener_disponibilidad(turno.profesional_id,turno.horario_turno,turno.especialidad.id,turno.paciente.id)
            dias_disponibles = [{
                "disponibilidad": disponibilidad
            }]
            return JsonResponse({
                "id": id_turno_medico,
                "profesional": f"{turno.profesional.persona.get_full_name()}",
                "matricula": turno.profesional.numero_matricula,
                "sexo": turno.profesional.persona.get_sexo_display(),
                "horario": "07:00 a 15:00" if turno.horario_turno == "dia" else "15:00 a 23:00" if turno.horario_turno == "tarde" else "Sin horario",
                "lugar": f"{turno.lugar.nombre} <br> <strong>(Piso: {turno.lugar.piso} - N° Sala: {turno.lugar.sala})</strong>",
                "fecha": turno.fecha_turno,
                "dias_disponibles": dias_disponibles
            })
        
        elif id_turno_estudio:
            
            if not TurnoEstudio.objects.filter(pk=id_turno_estudio,estado="pendiente").exists():
                response = render(request, "403.html", {
                    "mensaje": "Este turno no existe o ya fue atendidó."
                })
                response.status_code = 403
                return response  
                    
            turno = get_object_or_404(TurnoEstudio, pk=id_turno_estudio)
            
            # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
            if turno.orden.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.orden.paciente).exists():
                return HttpResponseForbidden(render(request, "403.html"))
            
            dias_disponibles, lugarDisponible = obtener_dias_disponibles_servicio(turno.servicio_diagnostico.id,turno.orden.paciente.id,turno.orden.tipo_estudio.id)
                
            data = {
                "id_orden": turno.orden.id,
                "nombre_estudio": turno.orden.tipo_estudio.nombre_estudio,
                "nombre_servicio": turno.orden.tipo_estudio.servicio_diagnostico.nombre_servicio,
                "fecha": turno.fecha_turno,
                "dias_disponibles": dias_disponibles
            }

            if lugarDisponible and dias_disponibles:
                data.update({
                    "lugar_id": lugarDisponible.id,
                    "lugar_nombre": lugarDisponible.nombre,
                    "lugar_piso": lugarDisponible.piso,
                    "lugar_sala": lugarDisponible.sala,
                    "horario": "7:00 a 15:00",
                    "disponible": True
                })
            else:
                data.update({
                    "lugar_disponible": False,
                    "mensaje": "No hay días disponibles para este servicio. Por favor, inténtelo nuevamente mañana.",
                    "disponible": False
                })
                
            return JsonResponse(data)
        
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)           
    
    
    
    hoy = timezone.localtime().date() 
    paciente = request.user.paciente
    turnos_anteriores = Turno.objects.filter(paciente_id=paciente, fecha_turno__lt=hoy).prefetch_related('consulta').order_by("-fecha_turno") # fecha_turno__lt=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea antes de hoy y con el orden_by ordenamos del más reciente al más viejo.
    turnos_futuros = Turno.objects.filter(paciente_id=paciente, fecha_turno__gte=hoy).order_by("fecha_turno") # fecha_turno__gte=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea hoy o en el futuro y con el orden_by ordenamos del más cercano al más lejos.
    
    turnosEstudios_anteriores = TurnoEstudio.objects.filter(orden__consulta__turno__paciente_id=paciente, fecha_turno__lt=hoy).order_by("-fecha_turno") # fecha_turno__lt=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea antes de hoy y con el orden_by ordenamos del más reciente al más viejo.
    turnosEstudios_futuros = TurnoEstudio.objects.filter(orden__consulta__turno__paciente_id=paciente, fecha_turno__gte=hoy).order_by("fecha_turno") # fecha_turno__gte=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea hoy o en el futuro y con el orden_by ordenamos del más cercano al más lejos.
    return render(request, "turnos/verTurnos.html",{"paciente":paciente,"turnos_anteriores":turnos_anteriores,"turnos_futuros":turnos_futuros, "turnosEstudios_futuros":turnosEstudios_futuros, "turnosEstudios_anteriores":turnosEstudios_anteriores}) 

@paciente_required
@login_required
def susTurnos(request, id_paciente):
    adulto = request.user.paciente
    
    if request.method == "GET" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        id_turno_medico = request.GET.get("id_turno_medico")
        id_turno_estudio = request.GET.get("id_turno_estudio")
        
        if id_turno_medico:
            if not Turno.objects.filter(pk=id_turno_medico,estado="pendiente").exists():
                response = render(request, "403.html", {
                    "mensaje": "Este turno no existe o ya fue atendidó."
                })
                response.status_code = 403
                return response    
            
            turno = get_object_or_404(Turno, id=id_turno_medico)
            
            # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
            if turno.paciente != adulto and not adulto.menores_a_cargo.filter(menor=turno.paciente).exists():
                return HttpResponseForbidden(render(request, "403.html"))
            
            disponibilidad = obtener_disponibilidad(turno.profesional_id,turno.horario_turno,turno.especialidad.id,turno.paciente.id)
            dias_disponibles = [{
                "disponibilidad": disponibilidad
            }]
            return JsonResponse({
                "id": id_turno_medico,
                "profesional": f"{turno.profesional.persona.get_full_name()}",
                "matricula": turno.profesional.numero_matricula,
                "sexo": turno.profesional.persona.get_sexo_display(),
                "horario": "07:00 a 15:00" if turno.horario_turno == "dia" else "15:00 a 23:00" if turno.horario_turno == "tarde" else "Sin horario",
                "lugar": f"{turno.lugar.nombre} <br> <strong>(Piso: {turno.lugar.piso} - N° Sala: {turno.lugar.sala})</strong>",
                "fecha": turno.fecha_turno,
                "dias_disponibles": dias_disponibles
            })
        
        elif id_turno_estudio:
            
            if not TurnoEstudio.objects.filter(pk=id_turno_estudio,estado="pendiente").exists():
                response = render(request, "403.html", {
                    "mensaje": "Este turno no existe o ya fue atendidó."
                })
                response.status_code = 403
                return response  
                    
            turno = get_object_or_404(TurnoEstudio, pk=id_turno_estudio)
            
            # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
            if turno.orden.paciente != adulto and not adulto.menores_a_cargo.filter(menor=turno.orden.paciente).exists():
                return HttpResponseForbidden(render(request, "403.html"))
            
            dias_disponibles, lugarDisponible = obtener_dias_disponibles_servicio(turno.servicio_diagnostico.id,turno.orden.paciente.id,turno.orden.tipo_estudio.id)
                
            data = {
                "id_orden": turno.orden.id,
                "nombre_estudio": turno.orden.tipo_estudio.nombre_estudio,
                "nombre_servicio": turno.orden.tipo_estudio.servicio_diagnostico.nombre_servicio,
                "fecha": turno.fecha_turno,
                "dias_disponibles": dias_disponibles
            }

            if lugarDisponible and dias_disponibles:
                data.update({
                    "lugar_id": lugarDisponible.id,
                    "lugar_nombre": lugarDisponible.nombre,
                    "lugar_piso": lugarDisponible.piso,
                    "lugar_sala": lugarDisponible.sala,
                    "horario": "7:00 a 15:00",
                    "disponible": True
                })
            else:
                data.update({
                    "lugar_disponible": False,
                    "mensaje": "No hay días disponibles para este servicio. Por favor, inténtelo nuevamente mañana.",
                    "disponible": False
                })
                
            return JsonResponse(data)
        
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)     
    
    hoy = timezone.localtime().date() 
    
    if not adulto.menores_a_cargo.filter(menor_id=id_paciente).exists():  # Si el usuario actual no tiene a cargo al menor que tiene el id que se pasa:
        return HttpResponseForbidden(render(request, "403.html"))  
    
    paciente = Paciente.objects.get(id=id_paciente) 
    turnos_anteriores = Turno.objects.filter(paciente_id=paciente, fecha_turno__lt=hoy).order_by("-fecha_turno") # fecha_turno__lt=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea antes de hoy y con el orden_by ordenamos del más reciente al más viejo.
    turnos_futuros = Turno.objects.filter(paciente_id=paciente, fecha_turno__gte=hoy).order_by("fecha_turno") # fecha_turno__gte=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea hoy o en el futuro y con el orden_by ordenamos del más cercano al más lejos.
    
    turnosEstudios_anteriores = TurnoEstudio.objects.filter(orden__consulta__turno__paciente_id=paciente, fecha_turno__lt=hoy).order_by("-fecha_turno") # fecha_turno__lt=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea antes de hoy y con el orden_by ordenamos del más reciente al más viejo.
    turnosEstudios_futuros = TurnoEstudio.objects.filter(orden__consulta__turno__paciente_id=paciente, fecha_turno__gte=hoy).order_by("fecha_turno") # fecha_turno__gte=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea hoy o en el futuro y con el orden_by ordenamos del más cercano al más lejos.
    
    return render(request, "turnos/verTurnos.html",{"paciente":paciente,"turnos_anteriores":turnos_anteriores,"turnos_futuros":turnos_futuros, "turnosEstudios_futuros":turnosEstudios_futuros, "turnosEstudios_anteriores":turnosEstudios_anteriores}) 


@paciente_required
@login_required
def seleccionarTurno(request,paciente_id):
    if request.user.paciente.id == paciente_id: # verifica si el usuario autenticado está intentando sacar turno para sí mismo
        paciente = get_object_or_404(Paciente, id=paciente_id)
    else:
        menores_a_cargo = request.user.paciente.menores_a_cargo.all()  # Obtiene los menores a cargo del paciente autenticado
        if not menores_a_cargo.filter(menor_id=paciente_id).exists(): # Verifica si el paciente_id no pertenece a alguno de esos menores
            return HttpResponseForbidden(render(request, "403.html"))
        else:
            menor = menores_a_cargo.get(menor_id=paciente_id)
            paciente = menor.menor
    
    orden_pendiente = OrdenEstudio.objects.filter(consulta__turno__paciente=paciente, estado="pendiente")
    return render(request, "turnos/seleccionarTipoTurno.html",{"orden_pendiente":orden_pendiente, "paciente":paciente}) 

@paciente_required
@login_required
def sacarTurno(request, paciente_id):
    parentesco = ""
    menor = False
    if request.user.paciente.id != paciente_id: # verifica si el usuario autenticado está intentando sacar turno para sí mismo
        menores_a_cargo = request.user.paciente.menores_a_cargo.all()  # Obtiene los menores a cargo del paciente autenticado
        if not menores_a_cargo.filter(menor_id=paciente_id).exists(): # Verifica si el paciente_id no pertenece a alguno de esos menores
            return HttpResponseForbidden(render(request, "403.html"))
        else:
            menor = menores_a_cargo.get(menor_id=paciente_id)
            parentesco = f"para {menor.menor.persona.get_full_name()} ({menor.get_parentesco_display()})"
    
    paciente = Paciente.objects.get(id=paciente_id)
        
    especialidades = Especialidades.objects.filter(permite_turno=True)
    dia = Jorna_laboral.objects.filter(turno="dia").first()
    tarde = Jorna_laboral.objects.filter(turno="tarde").first()
    horariosDeConsultas = [dia, tarde]
    
    if request.method == "GET":
        request.session.pop(f"especialidad_seleccionada_id_{paciente_id}", None)
        request.session.pop(f"horario_seleccionado_{paciente_id}", None)
    
    if request.method == "POST":
        tipo_form = request.POST.get("tipo_form")
        
        if tipo_form == "formSeleccionEspecialidad":
            estaBuscando = True
            especialidad_id = request.POST.get("especialidad")
            horario_turno = request.POST.get("horario")
            
            try:
                especialidad = Especialidades.objects.get(id=especialidad_id, permite_turno=True)
            except Especialidades.DoesNotExist:
                messages.error(request, "La especialidad seleccionada no es válida.")
                return render(request, "turnos/sacarTurno.html", {
                    "error": "Especialidad inválida",
                    "especialidades": especialidades,
                    "menor": menor,
                    "parentesco": parentesco,
                    "horariosDeConsultas": horariosDeConsultas
                })     
            
            # Guardar datos en sesión para validaciones posteriores
            request.session[f"especialidad_seleccionada_id_{paciente_id}"] = especialidad.id
            request.session[f"horario_seleccionado_{paciente_id}"] = horario_turno
            
            
            # Filtrar los profesionales que están asociados con la especialidad seleccionada
            profesionales = UsuarioRolProfesionalAsignado.objects.filter(rol_profesional__especialidad=especialidad, usuario__persona__is_active=True) 
            subConsulta = (  # Subconsulta que trae un registro de cada usuario.
                UsuarioLugarTrabajoAsignado.objects.filter(
                    usuario__in=profesionales.values('usuario'),
                    jornada__turno=horario_turno,
                    rolProfesionalAsignado__rol_profesional__especialidad= especialidad
                )
                .values('usuario')
                .annotate(min_id=Min('id'))
                .values('min_id')
            )
            profesionales_disponibles = UsuarioLugarTrabajoAsignado.objects.filter(id__in=subConsulta)
                    
            dias_disponibles = []
            formularios = [] 
            
            for profesional in profesionales_disponibles:
                disponibilidad = obtener_disponibilidad(profesional.usuario.id, horario_turno,especialidad.id,paciente.id)
                dias_disponibles.append({
                    "profesional": profesional.usuario.id,
                    "disponibilidad": disponibilidad
                })
                
                form = FormSacarTurno(initial={
                    'horario_turno': horario_turno,
                    'especialidad': especialidad.id,
                    'profesional': profesional.usuario.id,
                    'paciente': paciente.id,
                    'lugar': profesional.lugar.id
                })
                formularios.append({
                    "profesional": profesional,
                    "form": form
                })
            
            return render(request, "turnos/sacarTurno.html", {
                "estaBuscando":estaBuscando,
                "formularios" : formularios,
                "dias_disponibles": dias_disponibles,
                "menor":menor,
                "parentesco":parentesco,
                "especialidades": especialidades,
                "especialidadSeleccionada": especialidad,
                "horariosDeConsultas":horariosDeConsultas,
                "horarioSeleccionado": Jorna_laboral.objects.filter(turno=horario_turno).first()
            })
            
        elif tipo_form == "formSeleccionProfesional":
            form = FormSacarTurno(request.POST)
            
            try:
                paciente_form_id = int(request.POST.get("paciente"))
            except ValueError:
                response = render(request, "403.html", {
                    "mensaje": "El id del paciente no existe"
                })
                response.status_code = 403
                return response              
            try:
                profesional_form_id = int(request.POST.get("profesional"))
            except ValueError:
                response = render(request, "403.html", {
                    "mensaje": "El id del profesional no existe"
                })
                response.status_code = 403
                return response              
            try:
                especialidad_form_id = int(request.POST.get("especialidad"))
            except ValueError:
                response = render(request, "403.html", {
                    "mensaje": "El id de la especialidad no existe"
                })
                response.status_code = 403
                return response     
            try:
                lugar_form_id = int(request.POST.get("lugar"))
            except ValueError:
                response = render(request, "403.html", {
                    "mensaje": "El id del lugar no existe"
                })
                response.status_code = 403
                return response     
                        
            fecha_turno_form = request.POST.get("fecha_turno")
            fecha_turno_form = datetime.strptime(fecha_turno_form, "%Y-%m-%d").strftime("%Y-%m-%d")
            
            horario_turno_form = request.POST.get("horario_turno")         

            if paciente_form_id != paciente_id:
                response = render(request, "403.html", {
                    "mensaje": "No podés reservar un turno para otro paciente."
                })
                response.status_code = 403
                return response

            # Validar especialidad y coincidencia con la búsqueda
            try:
                especialidad_form = Especialidades.objects.get(id=especialidad_form_id, permite_turno=True)
            except Especialidades.DoesNotExist:
                response = render(request, "403.html", {
                    "mensaje": "Especialidad inválida o no disponible."
                })
                response.status_code = 403
                return response            

            especialidad_sesion = request.session.get(f"especialidad_seleccionada_id_{paciente_id}")
            if not especialidad_sesion or especialidad_sesion != especialidad_form.id:
                response = render(request, "403.html", {
                    "mensaje": "La especialidad no coincide con la seleccionada inicialmente."
                })
                response.status_code = 403
                return response                  

            # Validar horario
            horario_sesion = request.session.get(f"horario_seleccionado_{paciente_id}")
            if not horario_sesion or horario_turno_form != horario_sesion:
                response = render(request, "403.html", {
                    "mensaje": "El horario no coincide con el seleccionado inicialmente."
                })
                response.status_code = 403
                return response             

            # Validar profesional y su jornada
            try:
                profesional = UsuarioLugarTrabajoAsignado.objects.select_related("jornada", "usuario", "lugar").filter(usuario_id=profesional_form_id,usuario__persona__is_active=True).first()
            except UsuarioLugarTrabajoAsignado.DoesNotExist:
                response = render(request, "403.html", {
                    "mensaje": "Profesional inválido o no encontrado."
                })
                response.status_code = 403
                return response               
            

            if not UsuarioRolProfesionalAsignado.objects.filter(usuario=profesional.usuario, rol_profesional__especialidad=especialidad_form).exists():
                response = render(request, "403.html", {
                    "mensaje": "El profesional no pertenece a la especialidad seleccionada."
                })
                response.status_code = 403
                return response               

            if profesional.lugar.id != lugar_form_id :
                response = render(request, "403.html", {
                    "mensaje": "El lugar no coincide con donde trabaja el profesional."
                })
                response.status_code = 403
                return response             

            if profesional.jornada.turno != horario_turno_form :
                response = render(request, "403.html", {
                    "mensaje": "El horario no coincide con la jornada del profesional."
                })
                response.status_code = 403
                return response             

            # Validar fecha disponible
            disponibilidad = obtener_disponibilidad(profesional.usuario.id, horario_turno_form,especialidad_form.id,paciente.id)
            fechas_validas = [dia["fecha"] for dia in disponibilidad]
            if fecha_turno_form not in fechas_validas:
                response = render(request, "403.html", {
                    "mensaje": "Fecha de turno no válida para este profesional."
                })
                response.status_code = 403
                return response               

            if form.is_valid():
                turno = form.save()

                request.session.pop(f"especialidad_seleccionada_id_{paciente_id}", None)
                request.session.pop(f"horario_seleccionado_{paciente_id}", None)

                return redirect(reverse("turnoConfirmado", kwargs={"turno_id": turno.id}))
            else:
                messages.error(request, "Ha ocurrido un error al guardar el turno. Intentelo de nuevo")
    
    return render(request, "turnos/sacarTurno.html", {"especialidades": especialidades, "menor":menor,"parentesco":parentesco,"horariosDeConsultas":horariosDeConsultas})

@paciente_required
@login_required
def sacarTurnoEstudio(request, paciente_id):
    paciente_actual = request.user.paciente
    parentesco = ""
    menor = False
    if request.user.paciente.id != paciente_id: # verifica si el usuario autenticado está intentando sacar turno para sí mismo
        menores_a_cargo = request.user.paciente.menores_a_cargo.all()  # Obtiene los menores a cargo del paciente autenticado
        if not menores_a_cargo.filter(menor_id=paciente_id).exists(): # Verifica si el paciente_id no pertenece a alguno de esos menores
            return HttpResponseForbidden(render(request, "403.html"))
        else:
            menor = menores_a_cargo.get(menor_id=paciente_id)
            parentesco = f"para {menor.menor.persona.get_full_name()} ({menor.get_parentesco_display()})"
    
    verificarOrdenes = OrdenEstudio.objects.filter(paciente=paciente_id, estado="pendiente")
    for orden in verificarOrdenes:
        orden.marcar_vencida_si_corresponde()    
            
    estudios_solicitados = OrdenEstudio.objects.filter(paciente=paciente_id, estado="pendiente")
    
    if request.method == "GET" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        id_orden = request.GET.get("id_orden")
        orden = get_object_or_404(OrdenEstudio, id=id_orden)
        
        if id_orden:            
            if orden.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=orden.paciente).exists():  # Verificar que el turno pertenezca al paciente actual o a uno de sus menores a cargo
                return HttpResponseForbidden(render(request, "403.html")) 
            
            dias_disponibles, lugarDisponible = obtener_dias_disponibles_servicio(orden.tipo_estudio.servicio_diagnostico.id,orden.paciente.id,orden.tipo_estudio.id)
            
            data = {
                "id_orden": orden.id,
                "nombre_estudio": orden.tipo_estudio.nombre_estudio,
                "id_servicio": orden.tipo_estudio.servicio_diagnostico.id,
                "nombre_servicio": orden.tipo_estudio.servicio_diagnostico.nombre_servicio,
                "dias_disponibles": dias_disponibles
            }

            if lugarDisponible and dias_disponibles:
                data.update({
                    "lugar_id": lugarDisponible.id,
                    "lugar_nombre": lugarDisponible.nombre,
                    "lugar_piso": lugarDisponible.piso,
                    "lugar_sala": lugarDisponible.sala,
                    "horario": "7:00 a 15:00",
                    "disponible": True
                })
            else:
                data.update({
                    "lugar_disponible": False,
                    "mensaje": "No hay días disponibles para este servicio. Por favor, inténtelo nuevamente mañana.",
                    "disponible": False
                })
            
            return JsonResponse(data)
        
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)
    
    if request.method == "POST":
        form = FormSacarTurnoEstudio(request.POST)

        try:
            orden_form_id = int(request.POST.get("orden"))
        except ValueError:
            response = render(request, "403.html", {
                "mensaje": "El numero de orden es incorrecto"
            })
            response.status_code = 403
            return response    
        try:
            lugar_form_id = int(request.POST.get("lugar"))
        except ValueError:
            response = render(request, "403.html", {
                "mensaje": "Lugar no disponible"
            })
            response.status_code = 403
            return response                    
        try:
            servicio_form_id = int(request.POST.get("servicio_diagnostico"))
        except ValueError:
            response = render(request, "403.html", {
                "mensaje": "Servicio de diagnostico no disponible"
            })
            response.status_code = 403
            return response                    
        
        fecha_turno_form = request.POST.get("fecha_turno")
        fecha_turno_form = datetime.strptime(fecha_turno_form, "%Y-%m-%d").strftime("%Y-%m-%d")
        horario_turno_form = request.POST.get("horario_turno")  
        
        orden = OrdenEstudio.objects.get(pk=orden_form_id)    
        
        if orden.estado != "pendiente":
            response = render(request, "403.html", {
                "mensaje": "Esta orden ya fue programado o vencida."
            })
            response.status_code = 403
            return response      
            
        if orden.paciente.id != paciente_id:
            response = render(request, "403.html", {
                "mensaje": "No podés reservar un turno para otro paciente."
            })
            response.status_code = 403
            return response          
        
        if orden.tipo_estudio.servicio_diagnostico.id != servicio_form_id:
            response = render(request, "403.html", {
                "mensaje": "No podés reservar un turno en un servicio de diagnostico diferente."
            })
            response.status_code = 403
            return response          
        
        if not orden.tipo_estudio.servicio_diagnostico.lugar.filter(id=lugar_form_id).exists():
            response = render(request, "403.html", {
                "mensaje": "No podés reservar un turno en un lugar no capacitado para ese estudio."
            })
            response.status_code = 403
            return response          
        
        if horario_turno_form != "dia":
            response = render(request, "403.html", {
                "mensaje": "No podés reservar un turno en un horario diferente."
            })
            response.status_code = 403
            return response     
        
        disponibilidad, lugar = obtener_dias_disponibles_servicio(servicio_form_id,paciente_id,orden.tipo_estudio.id)
        fechas_validas = [dia["fecha"] for dia in disponibilidad]
        if fecha_turno_form not in fechas_validas:
            response = render(request, "403.html", {
                "mensaje": "Fecha de turno no disponible para este estudio."
            })
            response.status_code = 403
            return response       
        
        if form.is_valid():
            turno = form.save()
            orden.estado = "realizado"
            orden.save()
            return redirect(reverse("turnoEstudioConfirmado", kwargs={"turno_id": turno.id}))  # Redirigir a la vista de confirmación pasandole el id del turno recien creado
        else:
            messages.error(request, "Ha ocurrido un error al guardar el turno. Intentelo de nuevo")        
        
    return render(request, "turnos/sacarTurnoEstudio.html", {"estudios": estudios_solicitados, "menor": menor, "parentesco": parentesco,"form":FormSacarTurnoEstudio()})


@paciente_required
@login_required
def turno_confirmado(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)
    paciente_actual = request.user.paciente

    if turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.paciente).exists() or turno.estado != "pendiente":  # Verificar que el turno pertenezca al paciente actual o a uno de sus menores a cargo
        return HttpResponseForbidden(render(request, "403.html"))    
    
    if turno.estado != "pendiente":
        return HttpResponseForbidden(render(request, "403.html"))   
    
    es_menor = turno.paciente != request.user.paciente
    return render(request, "turnos/turnoConfirmado.html", {"datos_turno":turno, "is_menor":es_menor})

@paciente_required
@login_required
def turno_estudio_confirmado(request, turno_id):
    turnoEstudio = get_object_or_404(TurnoEstudio, id=turno_id)
    paciente_actual = request.user.paciente

    if turnoEstudio.orden.consulta.turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turnoEstudio.orden.consulta.turno.paciente).exists():  # Verificar que el turno pertenezca al paciente actual o a uno de sus menores a cargo
        return HttpResponseForbidden(render(request, "403.html"))    
    
    if turnoEstudio.estado != "pendiente":
        return HttpResponseForbidden(render(request, "403.html"))    
    
    es_menor = turnoEstudio.orden.consulta.turno.paciente != request.user.paciente
    return render(request, "turnos/turnoConfirmado.html", {"datos_turno":turnoEstudio, "is_menor":es_menor, "turnoEstudio":True})

@paciente_required
@login_required
def reprogramarTurno(request, turno_id):
    paciente_actual = request.user.paciente
    
    if not Turno.objects.filter(pk=turno_id,estado="pendiente").exists():
        response = render(request, "403.html", {
            "mensaje": "Este turno no existe o ya fue atendidó."
        })
        response.status_code = 403
        return response           
    
    turno = get_object_or_404(Turno, pk=turno_id)
    
    if request.method == 'GET':
        if turno.paciente != paciente_actual:    
            return redirect("susTurnos", id_paciente=turno.paciente.id)                        
        else:
            return redirect("misTurnos")     
    
    if request.method == "POST":
        
        # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
        if turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.paciente).exists():
            response = render(request, "403.html", {
                "mensaje": "Este turno es personal e intransferible. No es aplicable para el usuario actual ni para menores de edad dependientes."
            })
            response.status_code = 403
            return response  
            
        hoy = timezone.localtime()
        fecha_seleccionada = request.POST.get("fecha_seleccionada")   
        fecha_seleccionada = datetime.strptime(fecha_seleccionada, "%Y-%m-%d").strftime("%Y-%m-%d")
        
        # Validar fecha disponible
        disponibilidad = obtener_disponibilidad(turno.profesional.id, turno.horario_turno,turno.especialidad.id,turno.paciente.id)
        fechas_validas = [dia["fecha"] for dia in disponibilidad]

        if fecha_seleccionada not in fechas_validas:
            response = render(request, "403.html", {
                "mensaje": "Fecha de turno no válida para este profesional."
            })
            response.status_code = 403
            return response           
        
        try:
            with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                turno.fecha_creacion = hoy
                turno.fecha_turno = fecha_seleccionada
                turno.save()
                return redirect(reverse("turnoConfirmado", kwargs={"turno_id": turno.id})) 
        except Exception as e:
            messages.error(request, f"Ocurrió un error al reprogramar el turno: {str(e)}")             
            if turno.paciente != paciente_actual:    
                return redirect("susTurnos", id_paciente=turno.paciente.id)                        
            else:
                return redirect("misTurnos")                        
    
    return HttpResponseForbidden(render(request, "403.html"))


@paciente_required
@login_required
def cancelarTurno(request, turno_id):
    paciente_actual = request.user.paciente
    
    if not Turno.objects.filter(pk=turno_id,estado="pendiente").exists():
        response = render(request, "403.html", {
            "mensaje": "Este turno no existe o ya fue atendidó."
        })
        response.status_code = 403
        return response  

    turno = get_object_or_404(Turno, id=turno_id)
    
    # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
    if turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.paciente).exists():
        response = render(request, "403.html", {
            "mensaje": "Este turno es personal e intransferible. No es aplicable para el usuario actual ni para menores de edad dependientes."
        })
        response.status_code = 403
        return response  
    
    if turno.paciente == paciente_actual:  # Si el turno es del paciente actual
        if request.method == 'GET':
            return redirect("misTurnos")
        
        if request.method == 'POST':
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    turno.estado = "cancelado"
                    turno.asistio = False
                    turno.save()
                    messages.success(request, "Se canceló correctamente el turno.")                    
                    return redirect("misTurnos")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al cancelar el turno: {str(e)}")             
                return redirect("misTurnos")     
        
    
    menor_turno = paciente_actual.menores_a_cargo.filter(menor=turno.paciente).first() # Obtener el turno del menor relacionado
    if menor_turno: # Si el turno es de un menor a cargo
        if request.method == 'GET':
            return redirect(reverse("susTurnos", kwargs={"id_paciente": menor_turno.menor.id}))
    
        if request.method == 'POST':
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    turno.estado = "cancelado"
                    turno.asistio = False
                    turno.save()
                    messages.success(request, "Se canceló correctamente el turno.")                    
                    return redirect(reverse("susTurnos", kwargs={"id_paciente": menor_turno.menor.id}))
            except Exception as e:
                messages.error(request, f"Ocurrió un error al cancelar el turno: {str(e)}")             
                return redirect(reverse("susTurnos", kwargs={"id_paciente": menor_turno.menor.id}))
                
                        


@paciente_required
@login_required
def reprogramarTurnoEstudio(request, turno_id):
    paciente_actual = request.user.paciente
    
    if not TurnoEstudio.objects.filter(pk=turno_id,estado="pendiente").exists():
        response = render(request, "403.html", {
            "mensaje": "Este turno no existe o ya fue realizado."
        })
        response.status_code = 403
        return response 
    
    turno = get_object_or_404(TurnoEstudio, pk=turno_id)
    
    if request.method == 'GET':
        if turno.orden.paciente != paciente_actual:    
            return redirect("susTurnos", id_paciente=turno.orden.paciente.id)                        
        else:
            return redirect("misTurnos")       
    
    if request.method == "POST":
        
        # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
        if turno.orden.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.orden.paciente).exists():
            response = render(request, "403.html", {
                "mensaje": "Este turno es personal e intransferible. No es aplicable para el usuario actual ni para menores de edad dependientes."
            })
            response.status_code = 403
            return response  
        
        hoy = timezone.localtime()
        fechaSeleccionada = request.POST.get("fecha_seleccionadaEstudio") 
        fecha_seleccionada = datetime.strptime(fecha_seleccionada, "%Y-%m-%d").strftime("%Y-%m-%d")
                
        try:        
            lugarSeleccionado_id = int(request.POST.get("lugar"))
        except ValueError:
            response = render(request, "403.html", {
                "mensaje": "Lugar no disponible."
            })
            response.status_code = 403
            return response                
        
        disponibilidad, lugar = obtener_dias_disponibles_servicio(turno.servicio_diagnostico.id,turno.orden.paciente.id,turno.orden.tipo_estudio.id)
        fechas_validas = [dia["fecha"] for dia in disponibilidad]
        if fechaSeleccionada not in fechas_validas:
            response = render(request, "403.html", {
                "mensaje": "Fecha de turno no disponible para este estudio."
            })
            response.status_code = 403
            return response              
        
        if not turno.orden.tipo_estudio.servicio_diagnostico.lugar.filter(id=lugarSeleccionado_id).exists():
            response = render(request, "403.html", {
                "mensaje": "No podés reservar un turno en un lugar no capacitado para ese estudio."
            })
            response.status_code = 403
            return response         
        
        lugar = Lugar.objects.get(pk=lugarSeleccionado_id)   

        if TurnoEstudio.objects.filter(fecha_turno=fechaSeleccionada,servicio_diagnostico=turno.servicio_diagnostico,lugar=lugar).count() >= turno.servicio_diagnostico.capacidad_diaria:
            response = render(request, "403.html", {
                "mensaje": "No podés reservar un turno en un lugar sin disponibilidad."
            })
            response.status_code = 403
            return response      
            
        try:
            with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                turno.fecha_creacion = hoy
                turno.fecha_turno = fechaSeleccionada
                turno.lugar = lugar  
                # raise Exception("Forzando error para probar el except")                              
                turno.save()
                return redirect(reverse("turnoEstudioConfirmado", kwargs={"turno_id": turno.id}))  # Redirigir a la vista de confirmación pasandole el id del turno recien creado
        except Exception as e:
            messages.error(request, f"Ocurrió un error al reprogramar el turno: {str(e)}")             
            if turno.orden.paciente != paciente_actual:            
                return redirect("susTurnos", id_paciente=turno.orden.paciente.id)                        
            else:
                return redirect("misTurnos") 
    
    return HttpResponseForbidden(render(request, "403.html"))

@paciente_required
@login_required
def cancelarTurnoEstudio(request, turno_id):
    paciente_actual = request.user.paciente

    if not TurnoEstudio.objects.filter(pk=turno_id,estado="pendiente").exists():
        response = render(request, "403.html", {
            "mensaje": "Este turno no existe o ya fue atendidó."
        })
        response.status_code = 403
        return response  
    
    turno = get_object_or_404(TurnoEstudio, pk=turno_id)
    
    # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
    if turno.orden.consulta.turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.orden.consulta.turno.paciente).exists():
        response = render(request, "403.html", {
            "mensaje": "Este turno es personal e intransferible. No es aplicable para el usuario actual ni para menores de edad dependientes."
        })
        response.status_code = 403
        return response 
        
    if turno.orden.consulta.turno.paciente == paciente_actual:  # Si el turno es del paciente actual
        if request.method == 'GET':
            return redirect("misTurnos")
        
        if request.method == 'POST':     
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    turno.estado = "cancelado"
                    turno.asistio = False
                    turno.save()
                    messages.success(request, "Se canceló correctamente el turno.")                    
                    return redirect("misTurnos")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al cancelar el turno: {str(e)}")             
                return redirect("misTurnos")        
    
    menor_turno = paciente_actual.menores_a_cargo.filter(menor=turno.orden.consulta.turno.paciente).first() # Obtener el turno del menor relacionado
    if menor_turno: # Si el turno es de un menor a cargo
        if request.method == 'GET':
            return redirect(reverse("susTurnos", kwargs={"id_paciente": menor_turno.menor.id}))
    
        if request.method == 'POST':
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    turno.estado = "cancelado"
                    turno.save()
                    messages.success(request, "Se canceló correctamente el turno.")                    
                    return redirect(reverse("susTurnos", kwargs={"id_paciente": menor_turno.menor.id}))
            except Exception as e:
                messages.error(request, f"Ocurrió un error al cancelar el turno: {str(e)}")             
                return redirect(reverse("susTurnos", kwargs={"id_paciente": menor_turno.menor.id}))

@paciente_required
@login_required
def miHistorial(request):
    qs_base = Consultas.objects.filter(turno__paciente=request.user.paciente).prefetch_related('estudios', 'medicaciones')  # trae todas las medicaciones y estudios asociados a las consultas que hayas filtrado
    filtro = ConsultasFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    consultas = filtro.qs
    estudios = OrdenEstudio.objects.filter(consulta__turno__paciente = request.user.paciente)
    medicamentos = Medicaciones.objects.filter(consulta__turno__paciente = request.user.paciente)
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"tablasDinamicas/_tabla_consultas.html", {"allConsultas": consultas,"cantidad_registros_base":qs_base.count()})    
    
    if request.method == "GET":
        return render(request, "historialClinico.html",{"paciente":request.user.paciente,"allConsultas":consultas, "allEstudios":estudios, "allMedicamentos":medicamentos, "filtro":filtro,"cantidad_registros_base":qs_base.count()})

@paciente_required
@login_required
def suHistorial(request, id_paciente):
    adulto = request.user.paciente
    
    if not adulto.menores_a_cargo.filter(menor_id=id_paciente).exists():  # Si el usuario actual no tiene a cargo al menor que tiene el id que se pasa:
        return HttpResponseForbidden(render(request, "403.html"))  
    
    paciente = Paciente.objects.get(id=id_paciente) 
    qs_base = Consultas.objects.filter(turno__paciente=paciente).prefetch_related('estudios', 'medicaciones')  # trae todas las medicaciones y estudios asociados a las consultas que hayas filtrado
    filtro = ConsultasFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    consultas = filtro.qs
    estudios = OrdenEstudio.objects.filter(consulta__turno__paciente = paciente)
    medicamentos = Medicaciones.objects.filter(consulta__turno__paciente = paciente)
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"tablasDinamicas/_tabla_consultas.html", {"allConsultas": consultas,"cantidad_registros_base":qs_base.count()}) 
    
    return render(request, "historialClinico.html",{"paciente":paciente,"allConsultas":consultas, "allEstudios":estudios, "allMedicamentos":medicamentos,"filtro":filtro,"cantidad_registros_base":qs_base.count()})

@paciente_required
@login_required
def consultaEspecifica(request, id_turno):
    turno = get_object_or_404(Turno, id=id_turno)
    paciente_actual = request.user.paciente
    
    # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
    if turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.paciente).exists():
        return HttpResponseForbidden(render(request, "403.html"))
    
    consulta = Consultas.objects.filter(turno_id=turno.id,turno__paciente=turno.paciente).prefetch_related('estudios', 'medicaciones').first() # trae todas las medicaciones y estudios asociados a las consultas que hayas filtrado
    return render(request,"historialClinico.html",{"consultaEspecifica":consulta,"paciente":turno.paciente})

@paciente_required
@login_required
def resultadoEstudioEspecifico(request, id_turno):
    turno = get_object_or_404(TurnoEstudio, id=id_turno)
    paciente_actual = request.user.paciente
    
    # Verificar si el turno pertenece al paciente actual o a uno de sus menores a cargo
    if turno.orden.consulta.turno.paciente != paciente_actual and not paciente_actual.menores_a_cargo.filter(menor=turno.orden.consulta.turno.paciente).exists():
        return HttpResponseForbidden(render(request, "403.html"))
    
    resultadoEstudio = ResultadoEstudio.objects.get(turno_estudio_id=turno.id)
    return render(request,"historialClinico.html",{"resultadoEstudioEspecifico":resultadoEstudio})


@paciente_required
@login_required
def registrarMenor(request):
    adulto = request.user.paciente
    menores_relaciones = adulto.menores_a_cargo.select_related("menor__persona")
    if request.method == "GET":
        return render(request, "gestionMenores/registroMenor.html",{"form":RegistrarMenorForm(),"haveMenores":menores_relaciones})
    
    if request.method == "POST":
        form = RegistrarMenorForm(request.POST, adulto=request.user.paciente)
        if form.is_valid():
            form.save()
            return redirect("gestionMenores")
        else:
            return render(request, "gestionMenores/registroMenor.html", {"form": form})
        

@paciente_required
@login_required
def gestionMenores(request):
    adulto = request.user.paciente
    menores_relaciones = adulto.menores_a_cargo.select_related("menor__persona")
        
    if request.method == "GET" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        id_menor = request.GET.get("id")
        if id_menor:
            menor = get_object_or_404(MenorACargoDePaciente, menor_id=id_menor)
            data = {
                "id": id_menor,
                "dni": menor.menor.persona.dni,
                "nombre": menor.menor.persona.first_name,
                "apellido": menor.menor.persona.last_name,
                "sexo": menor.menor.persona.sexo,
                "fecha_nacimiento": menor.menor.persona.fecha_nacimiento,
                "parentesco": menor.parentesco
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400) 
    

    if request.method == "POST":
        tipo_form = request.POST.get("tipo_form")
        
        if tipo_form == "formEditMenor":
            id_menor = request.POST.get("id_menor")  
            if id_menor:
                try:
                    id_menor = int(id_menor)
                except (TypeError, ValueError):
                    id_menor = None
                    messages.error(request,"El campo tiene que ser un entero.")
                    return redirect("gestionMenores")
            else:
                messages.error(request,"El campo no debe estar vacio.")
                return redirect("gestionMenores")                
                                
            if id_menor is not None:
                menor = get_object_or_404(MenorACargoDePaciente, menor_id=id_menor)
                if not adulto.menores_a_cargo.filter(menor=menor.menor).exists():
                    response = render(request, "403.html", {
                        "mensaje": "No tienes acceso a este menor."
                    })
                    response.status_code = 403
                    return response             
                
                form = RegistrarMenorForm(request.POST, instance=menor.menor.persona, adulto=adulto)
                if form.is_valid():
                    form.save()  
                    messages.success(request,"Se editó correctamente los datos del menor.")
                    return redirect("gestionMenores")
                else:
                    return render(request, "gestionMenores/gestionMenores.html",{"menores_relaciones": menores_relaciones,"form":form,"error":True,"titleModal":"Editar Datos del Menor","id_paciente":menor.menor.id})  
            else:
                return redirect("gestionMenores")
            
        elif tipo_form == "formCancelarPago":
            id_paciente_persona = request.POST.get("id_paciente_persona")

            if id_paciente_persona:
                try:
                    id_paciente_persona = int(id_paciente_persona)
                except (TypeError, ValueError):
                    id_paciente_persona = None
                    messages.error(request,"El campo tiene que ser un entero.")
                    return redirect("gestionMenores")
            else:
                messages.error(request,"El campo no debe estar vacio.")
                return redirect("gestionMenores")                       

            if id_paciente_persona is not None:
                menor = get_object_or_404(Persona, pk=id_paciente_persona)
                if not adulto.menores_a_cargo.filter(menor=menor.paciente).exists():
                    response = render(request, "403.html", {
                        "mensaje": "No tienes acceso a este menor."
                    })
                    response.status_code = 403
                    return response    
            
                Turno.objects.filter(paciente=menor.paciente, estado="pendiente").update(estado="cancelado")
                TurnoEstudio.objects.filter(orden__paciente=menor.paciente, estado="pendiente").update(estado="cancelado")                                        

                menor.is_active = False;
                menor.save()
                messages.success(request,"La cuota hospitalaria del menor fue cancelada correctamente.")                                
                return redirect("gestionMenores")
            else:
                messages.error(request,"No fue posible cancelar la cuota hospitalaria del menor. Por favor, intente nuevamente")                
                return redirect("gestionMenores")
            
        elif tipo_form == "formReescribirMenor":
            id_paciente_persona = request.POST.get("id_paciente_persona")

            if id_paciente_persona:
                try:
                    id_paciente_persona = int(id_paciente_persona)
                except (TypeError, ValueError):
                    id_paciente_persona = None
                    messages.error(request,"El campo tiene que ser un entero.")
                    return redirect("gestionMenores")
            else:
                messages.error(request,"El campo no debe estar vacio.")
                return redirect("gestionMenores")                       

            if id_paciente_persona is not None:
                menor = get_object_or_404(Persona, pk=id_paciente_persona)
                if not adulto.menores_a_cargo.filter(menor=menor.paciente).exists():
                    response = render(request, "403.html", {
                        "mensaje": "No tienes acceso a este menor."
                    })
                    response.status_code = 403
                    return response    
            
                menor.is_active = True;
                menor.save()
                messages.success(request,"El pago de la cuota hospitalaria del menor se realizó correctamente.")                                
                return redirect("gestionMenores")
            else:
                messages.error(request,"No fue posible registrar el pago de la cuota hospitalaria del menor. Por favor, intente nuevamente")                
                return redirect("gestionMenores")
        
    return render(request, "gestionMenores/gestionMenores.html",{"menores_relaciones": menores_relaciones,"form":RegistrarMenorForm()})  

