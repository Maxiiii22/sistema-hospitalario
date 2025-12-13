from collections import defaultdict
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import superadmin_required # En controlUsuario.decorators creamos decoradores personalizados que verifiquen si el usuario tiene el atributo de paciente o usuario, y redirigirlo a una página de acceso denegado si intenta acceder a una vista que no le corresponde.
from hospital_personal.models import UsuarioLugarTrabajoAsignado,UsuarioRolProfesionalAsignado,Departamento,Especialidades,Turno,EstudiosDiagnosticos,TurnoEstudio,ServicioDiagnostico,Lugar,PlantillaEstudio,Jorna_laboral,AsignacionEnfermero,AsignacionMedico
from controlUsuario.models import Usuario,TiposUsuarios,RolesProfesionales,Persona
from hospital_pacientes.models import Paciente
from controlUsuario.forms import FormularioRegistroDePersonal
from hospital_personal.forms import FormEspecialidades,FormDepartamentos,FormTiposUsuarios,FormularioAsignaciones,FormularioLugarTrabajo,FormRolesProfesionales,FormServiciosDiagnostico,FormEstudiosDiagnosticos,FormLugar,FormPlantillaEstudio,FormularioEditarLugarTrabajo
from hospital_personal.filters import LugarFilter,PacienteFilter,UsuarioFilter, EspecialidadesFilter, ServiciosFilter, EstudiosFilter, PlantillaEstudioFilter, DepartamentosFilter, RolesProfesionalesFilter
from django.db.models.functions import Cast
from django.db.models import Max, IntegerField
from datetime import datetime
from django.utils import timezone
from django.db import transaction



@superadmin_required
@login_required
def gestionDelPersonal(request):
    qs_base = Usuario.objects.all()
    filtro = UsuarioFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    personal = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_personal.html", {"allPersonal": personal,"filtro":filtro,"cantidad_registros_base":qs_base.count()})   
    
    return render(request, "superadmin/gestionPersonal/gestionPersonal.html", {"allPersonal":personal,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@superadmin_required
@login_required
def altaPersonal(request):
    ultimo_login_id = (
        Persona.objects
        .filter(login_id__regex=r'^\d+$')  # Solo login_id numéricos
        .annotate(login_id_num=Cast('login_id', IntegerField()))
        .aggregate(max_id=Max('login_id_num'))['max_id'] or 999
    )

    siguiente_login_id = ultimo_login_id + 1
    formUsuario = FormularioRegistroDePersonal()

    if request.method == "POST":
        formUsuario = FormularioRegistroDePersonal(request.POST)
        
        # Validar que los formularios internos son válidos
        if formUsuario.is_valid() and formUsuario.persona_form.is_valid() and formUsuario.usuario_form.is_valid():                
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    persona = formUsuario.persona_form.save(commit=False)  
                    
                    # Establecer la contraseña de forma segura (hash)
                    persona.set_password(formUsuario.persona_form.cleaned_data['password'])
                    persona.save() 
                    
                    usuario = formUsuario.usuario_form.save(commit=False)  
                    usuario.persona = persona  
                    usuario.save()  

                    messages.success(request, "El personal ha sido registrado correctamente.")
                    return redirect('detalle_usuario', id=usuario.id)                        
            except Exception as e:
                messages.error(request, f"Ocurrió un error al guardar el usuario. Intenta nuevamente. ({e})")                
        else:
            messages.error(request, "Formulario inválido. Revisa los datos ingresados.") 

    return render(request, "superadmin/gestionPersonal/altaPersona.html", {"formUsuario": formUsuario,"lastLogin_id": siguiente_login_id})

@superadmin_required
@login_required
def detalle_usuario(request,id):
    if not Usuario.objects.filter(pk=id).exists():
        response = render(request, "403.html", {
            "mensaje": "Este usuario no existe"
        })
        response.status_code = 403
        return response      
    
    usuario = Usuario.objects.get(pk=id)
    
    if usuario != request.user.usuario and not request.user.is_staff: 
        return HttpResponseForbidden(render(request, "403.html"))
    
    rolesProfesionales = UsuarioRolProfesionalAsignado.objects.filter(usuario_id=id)
    asignacionesDeLugarDeTrabajo = UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=id).order_by('jornada')

    departamentos_con_jornadas = defaultdict(list)

    for asignacion in asignacionesDeLugarDeTrabajo:
        especialidad_o_servicio = (
            getattr(asignacion.rolProfesionalAsignado.rol_profesional.especialidad, 'nombre_especialidad', None)
            or getattr(asignacion.rolProfesionalAsignado.rol_profesional.servicio_diagnostico, 'nombre_servicio', None)
        )  

        if asignacion.rolProfesionalAsignado.rol_profesional.tipoUsuario.id == 7:  # Si es jefe de enfermería
            rolProfesional = f"{asignacion.rolProfesionalAsignado.rol_profesional.tipoUsuario} ({asignacion.rolProfesionalAsignado.rol_profesional.nombre_rol_profesional})"
        else:
            rolProfesional = asignacion.rolProfesionalAsignado.rol_profesional.nombre_rol_profesional   

        if asignacion.estado == "asignado":
            info = (
                f"Los días <strong>{asignacion.jornada.get_dia_display()}</strong> "
                f"en el turno: <strong>{asignacion.jornada.get_turno_display()}</strong> "
                f"trabaja en el <strong>{asignacion.lugar.nombre} ({asignacion.lugar.abreviacion})</strong> "
                f"como <strong>{rolProfesional}"
            )
            if especialidad_o_servicio:
                info += f" (En {especialidad_o_servicio})"
            info += "</strong>"
        else:
            info = (
                f"Los días <strong>{asignacion.jornada.get_dia_display()}</strong> "
                f"en el turno: <strong>{asignacion.jornada.get_turno_display()}</strong> "
                "estan <strong>Desasignados</strong>. La asignación de trabajo podrá editarse/eliminarse una vez "
                "transcurrida la fecha del último turno programado del médico."
            )
        
        departamentos_con_jornadas[asignacion.lugar.departamento].append({
            "id": f"{asignacion.id}",
            "info": info,
            "estado": f"{asignacion.estado}"
        })
        
    
    departamentos_con_jornadas = dict(departamentos_con_jornadas)
    formUsuario = FormularioRegistroDePersonal(persona_instance=usuario.persona,usuario_instance=usuario)
    formAsignaciones = FormularioAsignaciones(user=usuario,initial={"usuario":usuario.id})
    formLugarTrabajo = FormularioLugarTrabajo(usuario=usuario,initial={"id_usuario":usuario.id})
    formEditarLugarTrabajo = FormularioEditarLugarTrabajo(usuario=usuario,initial={"usuario":usuario.id})
    
    if request.method == 'POST':
        tipo_form = request.POST.get("tipo_form")
        
        if tipo_form == "form_editarPersonal":
            formUsuario = FormularioRegistroDePersonal(
                request.POST,
                persona_instance=usuario.persona,
                usuario_instance=usuario
            )
            if formUsuario.is_valid():
                usuario_guardado = formUsuario.save(commit=True)  
                return redirect('detalle_usuario', id=usuario_guardado.id)  
            
        elif tipo_form == "form_asignaciones": # Asignacion de roles profesionales
            asignacion_id = request.POST.get("id_instancia") 
            
            if asignacion_id:  # EDICIÓN
                if not UsuarioRolProfesionalAsignado.objects.filter(pk=asignacion_id,usuario=usuario).exists():
                    response = render(request, "403.html", {
                        "mensaje": "Esta asignacion no le corresponde a este usuario."
                    })
                    response.status_code = 403
                    return response
                
                asignacion_existente = UsuarioRolProfesionalAsignado.objects.get(pk=asignacion_id)
                formAsignaciones = FormularioAsignaciones(request.POST, user=usuario, instance=asignacion_existente, initial={"usuario":usuario.id,"id_instancia":asignacion_existente.id})
                titleModal = "Editar rol profesional"
            else:  # ALTA
                formAsignaciones = FormularioAsignaciones(request.POST, user=usuario, initial={"usuario":usuario.id})    
                titleModal = "Asignar nuevo rol profesional"        

            
            if formAsignaciones.is_valid():
                asignacion = formAsignaciones.save(commit=False)
                asignacion.save()
                return redirect('detalle_usuario', id=usuario.id) 
            else:
                return render(request, "superadmin/gestionPersonal/detallesUsuario.html",{
                            "usuario":usuario,"rolesProfesionales":rolesProfesionales,"departamentos_con_jornadas": departamentos_con_jornadas,
                            "formUsuario":formUsuario,
                            "formAsignaciones": formAsignaciones,"formLugarTrabajo": formLugarTrabajo,
                            "formEditarLugarTrabajo":formEditarLugarTrabajo,
                            "errorFormAsignaciones": True,
                            "titleModal":titleModal})  
            
        elif tipo_form == "form_lugarTrabajo":            
            formLugarTrabajo = FormularioLugarTrabajo(request.POST, usuario=usuario,initial={"id_usuario":usuario.id})  
            
            if formLugarTrabajo.is_valid():
                creados, omitidos = formLugarTrabajo.save()
                
                if omitidos:
                    jornadas_texto = ", ".join(f"{j.get_dia_display()} - {j.get_turno_display()}" for j in omitidos)
                    messages.info(request, f"Estas jornadas ya estaban asignadas al usuario y fueron omitidas: {jornadas_texto}")
                
                if creados:
                    messages.success(request, f"Se asignaron correctamente {len(creados)} jornada(s) nuevas al usuario.")
                    
                return redirect('detalle_usuario', id=usuario.id)
            else:
                return render(request, "superadmin/gestionPersonal/detallesUsuario.html",{
                            "usuario":usuario,"rolesProfesionales":rolesProfesionales,"departamentos_con_jornadas": departamentos_con_jornadas,
                            "formUsuario":formUsuario,
                            "formAsignaciones": formAsignaciones,"formLugarTrabajo": formLugarTrabajo,
                            "formEditarLugarTrabajo":formEditarLugarTrabajo,
                            "errorFormLugarTrabajo": True,
                            "titleModal":"Asignar nuevo lugar de trabajo"})  
                
        elif tipo_form == "form_solicitarEditarLugarTrabajo":
            id_instancia = request.POST.get('id_instancia')
            if not UsuarioLugarTrabajoAsignado.objects.filter(pk=id_instancia,usuario=usuario).exists():
                response = render(request, "403.html", {
                    "mensaje": "Esta asignacion no le corresponde a este usuario."
                })
                response.status_code = 403
                return response                
                            
            instancia = get_object_or_404(UsuarioLugarTrabajoAsignado, pk=id_instancia)
                            
            if instancia.usuario.tipoUsuario.id == 3:
                if Turno.objects.filter(profesional=instancia.usuario,horario_turno=instancia.jornada.turno,fecha_turno__gte=timezone.localtime().date()).exists():
                    turnos = Turno.objects.filter(profesional=instancia.usuario,horario_turno=instancia.jornada.turno,fecha_turno__gte=timezone.localtime().date())
                    for turno in turnos:
                        fecha = datetime(turno.fecha_turno.year,turno.fecha_turno.month,turno.fecha_turno.day)
                        nombre_dia = fecha.strftime('%A').lower()                    
                        dias_en_espanol = {
                            "monday": "lunes",
                            "tuesday": "martes",
                            "wednesday": "miercoles",
                            "thursday": "jueves",
                            "friday": "viernes",
                            "saturday": "sabado",
                            "sunday": "domingo"
                        }
                        dia_semana = dias_en_espanol.get(nombre_dia, "")
                        if dia_semana == instancia.jornada.dia:
                            if instancia.estado == "asignado":
                                instancia.estado = "desasignado"
                                instancia.save()
                                messages.success(request, "El día ha sido desasignado correctamente. La asignación de trabajo podrá editarse una vez transcurrida la fecha del último turno programado del médico.")
                            else: 
                                messages.info(request, "Este día ya ha sido anteriormente desasignado correctamente. La asignación de trabajo podrá editarse una vez transcurrida la fecha del último turno programado del médico.")
                            
                            return redirect('detalle_usuario', id=instancia.usuario.id)
                else:
                    messages.success(request, "No hay turnos")
                    return redirect('detalle_usuario', id=instancia.usuario.id)
                
        elif tipo_form == "form_editarLugarTrabajo":
                id_instancia = request.POST.get('id_instancia')
                if not UsuarioLugarTrabajoAsignado.objects.filter(pk=id_instancia,usuario=usuario).exists():
                    response = render(request, "403.html", {
                        "mensaje": "Esta asignacion no le corresponde a este usuario."
                    })
                    response.status_code = 403
                    return response                
                
                instancia = get_object_or_404(UsuarioLugarTrabajoAsignado, pk=id_instancia)
                
                
                if instancia.usuario.tipoUsuario.id == 3:
                    if Turno.objects.filter(profesional=instancia.usuario,horario_turno=instancia.jornada.turno,fecha_turno__gte=timezone.localtime().date()).exists():
                        turnos = Turno.objects.filter(profesional=instancia.usuario,horario_turno=instancia.jornada.turno,fecha_turno__gte=timezone.localtime().date())
                        for turno in turnos:
                            fecha = datetime(turno.fecha_turno.year,turno.fecha_turno.month,turno.fecha_turno.day)
                            nombre_dia = fecha.strftime('%A').lower()                    
                            dias_en_espanol = {
                                "monday": "lunes",
                                "tuesday": "martes",
                                "wednesday": "miercoles",
                                "thursday": "jueves",
                                "friday": "viernes",
                                "saturday": "sabado",
                                "sunday": "domingo"
                            }
                            dia_semana = dias_en_espanol.get(nombre_dia, "")
                            if dia_semana == instancia.jornada.dia:
                                messages.info(request, "No puede editarse esta asignacion ya que hay turnos programados")
                                return redirect('detalle_usuario', id=instancia.usuario.id)
                
                elif UsuarioLugarTrabajoAsignado.objects.filter(usuario=instancia.usuario,jornada=instancia.jornada).exists():
                    if instancia.usuario.tipoUsuario.id == 4:
                        if AsignacionEnfermero.objects.filter(enfermero=instancia.usuario,asignacion_habitacion__estado="finalizada").exists():
                            messages.info(request, "Este enfermero posee asignaciones hospitalarias vigentes. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de ese modo, poder editar la asignación de trabajo.")               
                            return redirect('detalle_usuario', id=instancia.usuario.id)
                        
                    elif instancia.usuario.tipoUsuario.id == 8 :
                        if AsignacionMedico.objects.filter(medico=instancia.usuario,asignacion_habitacion__estado="activa").exists():
                            messages.info(request, "Este médico posee asignaciones hospitalarias vigentes. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de ese modo, poder editar la asignación de trabajo.")
                            return redirect('detalle_usuario', id=instancia.usuario.id)
                
                formEditarLugarTrabajo = FormularioEditarLugarTrabajo(request.POST, instance=instancia, usuario=usuario,initial={"usuario":usuario.id,"id_instancia":instancia.id})
                if formEditarLugarTrabajo.is_valid():
                    formEditarLugarTrabajo.save()
                    messages.success(request, "Lugar de trabajo actualizado correctamente.")
                    return redirect('detalle_usuario', id=instancia.usuario.id)
                else:
                    return render(request, "superadmin/gestionPersonal/detallesUsuario.html",{
                                "usuario":usuario,"rolesProfesionales":rolesProfesionales,"departamentos_con_jornadas": departamentos_con_jornadas,
                                "formUsuario":formUsuario,
                                "formAsignaciones": formAsignaciones,"formLugarTrabajo": formLugarTrabajo,
                                "formEditarLugarTrabajo":formEditarLugarTrabajo,
                                "errorFormEditarLugarTrabajo": True,
                                "titleModal":"Editar lugar de trabajo"}) 
                    

    return render(request, "superadmin/gestionPersonal/detallesUsuario.html",{"usuario":usuario,"rolesProfesionales":rolesProfesionales,"departamentos_con_jornadas": departamentos_con_jornadas,
                    "formUsuario":formUsuario,
                    "formAsignaciones": formAsignaciones,"formLugarTrabajo": formLugarTrabajo, "formEditarLugarTrabajo": formEditarLugarTrabajo  }) 

@superadmin_required
@login_required
def getLugarTrabajoDisponibilidad(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_lugar = request.GET.get('id')
        id_usuario = request.GET.get('usuario_id')
        
        if id_lugar and id_usuario:
            lugar = get_object_or_404(Lugar, id=id_lugar)
            jornadas = Jorna_laboral.objects.all()
            usuario = get_object_or_404(Usuario,id=id_usuario)
            
            disponibilidad_de_jornadas = defaultdict(list)
            for jornada in jornadas:
                estado, cantidad = lugar.estado_por_jornada(jornada)
                msg = jornada.jornadaDisponible(usuario,lugar)
                
                disponibilidad_de_jornadas[jornada.id].append({
                    "id": f"{jornada.id}",
                    "estado": estado,
                    "cantidad": cantidad,
                    "maxCantidad": f"{lugar.capacidad}",
                    "Disponible": msg
                })

            data = {
                "disponibilidad": disponibilidad_de_jornadas,           
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

@superadmin_required
@login_required
def getLugarTrabajoORolProfesional(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_lugarTrabajo = request.GET.get('id_lugarTrabajo')
        id_rolProfesional = request.GET.get('id_rolProfesional')
        
        if id_lugarTrabajo:
            lugarTrabajo = get_object_or_404(UsuarioLugarTrabajoAsignado, id=id_lugarTrabajo)
            mensaje=None
            estado=None
            sinTurno = False
            
            if lugarTrabajo.usuario.tipoUsuario.id == 3:
                fechas = []   
                turnos = Turno.objects.filter(profesional=lugarTrabajo.usuario,horario_turno=lugarTrabajo.jornada.turno,fecha_turno__gte=timezone.localtime().date())
                for turno in turnos:
                    fecha = datetime(turno.fecha_turno.year,turno.fecha_turno.month,turno.fecha_turno.day)
                    nombre_dia = fecha.strftime('%A').lower()                    
                    dias_en_espanol = {
                        "monday": "lunes",
                        "tuesday": "martes",
                        "wednesday": "miercoles",
                        "thursday": "jueves",
                        "friday": "viernes",
                        "saturday": "sabado",
                        "sunday": "domingo"
                    }
                    dia_semana = dias_en_espanol.get(nombre_dia, "")
                    if dia_semana == lugarTrabajo.jornada.dia:                        
                        fechas.append(turno.fecha_turno)
                    
                if fechas:                
                    data = {
                        "id_instancia_solicitud": lugarTrabajo.id,
                        "sinTurno": sinTurno,
                        "fecha": max(fechas).strftime("%d-%m-%Y"),
                        "estado": f"{lugarTrabajo.estado}"
                    }
                    return JsonResponse(data)                    
                else:
                    sinTurno = True
                                        
            elif lugarTrabajo.usuario.tipoUsuario.id == 4:
                if UsuarioLugarTrabajoAsignado.objects.filter(usuario=lugarTrabajo.usuario,jornada=lugarTrabajo.jornada).exists():
                    if AsignacionEnfermero.objects.filter(enfermero=lugarTrabajo.usuario,asignacion_habitacion__estado="activa").exists():
                        mensaje = "Este enfermero posee asignaciones hospitalarias vigentes en este día. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de este modo, poder editar la asignación de trabajo."
                        estado = "activa"
                    
            elif lugarTrabajo.usuario.tipoUsuario.id == 8:
                if UsuarioLugarTrabajoAsignado.objects.filter(usuario=lugarTrabajo.usuario,jornada=lugarTrabajo.jornada).exists():                
                    if AsignacionMedico.objects.filter(medico=lugarTrabajo.usuario,asignacion_habitacion__estado="activa").exists():
                        mensaje = "Este médico posee asignaciones hospitalarias vigentes en este día. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de ese modo, poder editar la asignación de trabajo."
                        estado = "activa"

            data = {
                "id_instancia": lugarTrabajo.id,
                "id_lugar": lugarTrabajo.lugar.id,
                "id_jornada": lugarTrabajo.jornada.id,            
                "id_rolProfesionalAsignado": lugarTrabajo.rolProfesionalAsignado.id,    
                "sinTurno": sinTurno,
                "mensaje": mensaje,
                "estado": estado
            }
            return JsonResponse(data)
        
        elif id_rolProfesional:
            rolProfesional = get_object_or_404(UsuarioRolProfesionalAsignado, id=id_rolProfesional)
            data = {
                "id_instancia": rolProfesional.id,
                "id_rolProfesional": getattr(rolProfesional.rol_profesional, 'id', None),            
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

@superadmin_required
@login_required
def deleteLugarTrabajo(request,id_lugarTrabajo):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_lugarTrabajo = request.GET.get('id_lugarTrabajo')
        if id_lugarTrabajo:
            mensaje = None
            estado = None
            lugarTrabajo = get_object_or_404(UsuarioLugarTrabajoAsignado, id=id_lugarTrabajo)
            if lugarTrabajo.usuario.tipoUsuario.id == 3:
                fechas = []   
                turnos = Turno.objects.filter(profesional=lugarTrabajo.usuario,horario_turno=lugarTrabajo.jornada.turno,fecha_turno__gte=timezone.localtime().date())
                for turno in turnos:
                    fecha = datetime(turno.fecha_turno.year,turno.fecha_turno.month,turno.fecha_turno.day)
                    nombre_dia = fecha.strftime('%A').lower()                    
                    dias_en_espanol = {
                        "monday": "lunes",
                        "tuesday": "martes",
                        "wednesday": "miercoles",
                        "thursday": "jueves",
                        "friday": "viernes",
                        "saturday": "sabado",
                        "sunday": "domingo"
                    }
                    dia_semana = dias_en_espanol.get(nombre_dia, "")
                    if dia_semana == lugarTrabajo.jornada.dia:                        
                        fechas.append(turno.fecha_turno)
                    
                if fechas:                
                    data = {
                        "fecha": max(fechas).strftime("%d-%m-%Y"),
                        "estado": f"{lugarTrabajo.estado}"
                    }
                else:
                    data = {
                        "mensaje": "Está seguro que desea desasignar y eliminar de inmediato el trabajo del usuario en este día? Esta acción se realizará de forma instantánea, ya que el médico no tiene turnos futuros programados."
                    }
                
            elif lugarTrabajo.usuario.tipoUsuario.id == 4:
                if UsuarioLugarTrabajoAsignado.objects.filter(usuario=lugarTrabajo.usuario,jornada=lugarTrabajo.jornada).exists():
                    if AsignacionEnfermero.objects.filter(enfermero=lugarTrabajo.usuario,asignacion_habitacion__estado="activa").exists():                        
                        mensaje = "Este enfermero posee asignaciones hospitalarias vigentes en este día. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de ese modo, habilitar la eliminación de la asignación de trabajo."
                        estado = "activa"                        
                    else:
                        mensaje = "Está seguro que desea desasignar y eliminar de inmediato el trabajo del usuario en este día? Esta acción se realizará de forma instantánea, ya que el enfermero no posee asignaciones hospitalarias vigentes."
                        estado = "finalizada"
                    data = {
                        "mensaje": mensaje,
                        "estado": estado
                    }
                    
            elif lugarTrabajo.usuario.tipoUsuario.id == 8:
                if UsuarioLugarTrabajoAsignado.objects.filter(usuario=lugarTrabajo.usuario,jornada=lugarTrabajo.jornada).exists():                
                    if AsignacionMedico.objects.filter(medico=lugarTrabajo.usuario,asignacion_habitacion__estado="activa").exists():
                        mensaje =  "Este médico posee asignaciones hospitalarias vigentes en este día. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de ese modo, habilitar la eliminación de la asignación de trabajo."
                        estado = "activa"
                    else:
                        mensaje = "Está seguro que desea desasignar y eliminar de inmediato el trabajo del usuario en este día? Esta acción se realizará de forma instantánea, ya que el médico no posee asignaciones hospitalarias vigentes."
                        estado = "finalizada"                        
                    data = {
                        "mensaje": mensaje,
                        "estado": estado                        
                    }                    
            
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)    

    
    lugarTrabajo = get_object_or_404(UsuarioLugarTrabajoAsignado, id=id_lugarTrabajo)
    usuario_id = lugarTrabajo.usuario.id
    
    if request.method == 'GET':
        return redirect('detalle_usuario', id=usuario_id)
        
    if request.method == 'POST':
        if lugarTrabajo.usuario.tipoUsuario.id == 3:
            if Turno.objects.filter(profesional=lugarTrabajo.usuario,horario_turno=lugarTrabajo.jornada.turno,fecha_turno__gte=timezone.localtime().date()).exists():
                turnos = Turno.objects.filter(profesional=lugarTrabajo.usuario,horario_turno=lugarTrabajo.jornada.turno,fecha_turno__gte=timezone.localtime().date())
                for turno in turnos:
                    fecha = datetime(turno.fecha_turno.year,turno.fecha_turno.month,turno.fecha_turno.day)
                    nombre_dia = fecha.strftime('%A').lower()                    
                    dias_en_espanol = {
                        "monday": "lunes",
                        "tuesday": "martes",
                        "wednesday": "miercoles",
                        "thursday": "jueves",
                        "friday": "viernes",
                        "saturday": "sabado",
                        "sunday": "domingo"
                    }
                    dia_semana = dias_en_espanol.get(nombre_dia, "")
                    if dia_semana == lugarTrabajo.jornada.dia:
                        if lugarTrabajo.estado == "asignado":
                            lugarTrabajo.estado = "desasignado"
                            lugarTrabajo.save()
                            messages.success(request, "El día ha sido desasignado correctamente. La asignación de trabajo podrá eliminarse una vez transcurrida la fecha del último turno programado del médico.")
                        else: 
                            messages.success(request, "Este día ya ha sido desasignado correctamente. La asignación de trabajo podrá eliminarse una vez transcurrida la fecha del último turno programado del médico.")
                            
                        return redirect('detalle_usuario', id=usuario_id)
                                    
                lugarTrabajo.delete()     
            else:
                lugarTrabajo.delete()
            messages.success(request, "La asignación de trabajo ha sido desasignada y eliminada correctamente.")
            
        elif lugarTrabajo.usuario.tipoUsuario.id == 4:
            if UsuarioLugarTrabajoAsignado.objects.filter(usuario=lugarTrabajo.usuario,jornada=lugarTrabajo.jornada).exists():
                if AsignacionEnfermero.objects.filter(enfermero=lugarTrabajo.usuario,asignacion_habitacion__estado="activa").exists():
                    messages.info(request, "Este enfermero posee asignaciones hospitalarias vigentes. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de ese modo, habilitar la eliminación de la asignación de trabajo.")
                else:
                    lugarTrabajo.delete()
                    messages.success(request, "La asignación de trabajo ha sido desasignada y eliminada correctamente.")
            else:
                messages.info(request, "Este usuario no trabaja en esa asignacion")                      
    
        elif lugarTrabajo.usuario.tipoUsuario.id == 8:
            if UsuarioLugarTrabajoAsignado.objects.filter(usuario=lugarTrabajo.usuario,jornada=lugarTrabajo.jornada).exists():            
                if AsignacionMedico.objects.filter(medico=lugarTrabajo.usuario,asignacion_habitacion__estado="activa").exists():
                    messages.info(request, "Este médico posee asignaciones hospitalarias vigentes. Por favor, comuníquese con su jefe de enfermería para que gestione su desasignación y, de ese modo, habilitar la eliminación de la asignación de trabajo.")
                else:
                    lugarTrabajo.delete()
                    messages.success(request, "La asignación de trabajo ha sido desasignada y eliminada correctamente.")  
            else:
                messages.info(request, "Este usuario no trabaja en esa asignacion")  
            
        return redirect('detalle_usuario', id=usuario_id)

@superadmin_required
@login_required
def deleteRolProfesionalAsignado(request,id_rolProfesionalAsignado):
    
    rolProfesionalAsignado = get_object_or_404(UsuarioRolProfesionalAsignado, pk=id_rolProfesionalAsignado)
    usuario_id = rolProfesionalAsignado.usuario.id
    
    if rolProfesionalAsignado.RolesProfesionalesAsignados.exists():
        messages.info(request, "No es posible eliminar este rol porque tiene lugares de trabajo asignados.")
        return redirect('detalle_usuario', id=usuario_id)
    
    if request.method == 'GET':
        return redirect('detalle_usuario', id=usuario_id)
    
    if request.method == 'POST':
        rolProfesionalAsignado.delete()
        return redirect('detalle_usuario', id=usuario_id)


@superadmin_required
@login_required
def gestionDeDepartamentos(request):
    formDepartamentos = FormDepartamentos()
    
    qs_base = Departamento.objects.all()
    filtro = DepartamentosFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    departamentos = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_departamentos.html", {"allDepartamentos": departamentos,"filtro":filtro,"cantidad_registros_base":qs_base.count()})

        id = request.GET.get('id')
        if id:
            departamento = get_object_or_404(Departamento, id=id)
            data = {
                "id_departamento": departamento.id,
                "nombre_departamento": departamento.nombre_departamento,
                "tipo": departamento.tipo,
                "descripcion": departamento.descripcion
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)
    
    if request.method == "POST":
        id_departamento = request.POST.get('id_departamento')
        mensaje=""
        if id_departamento:
            departamento = get_object_or_404(Departamento, id=id_departamento)
            formDepartamentos = FormDepartamentos(request.POST, instance=departamento)
            mensaje = "Se editó correctamente el departamento."
        else:
            formDepartamentos = FormDepartamentos(request.POST)
            mensaje = "Se añadió correctamente el departamento"
            
        if formDepartamentos.is_valid():
            formDepartamentos.save()
            messages.succes(request, mensaje)             
            return redirect("gestionDeDepartamentos")  
        else:
            messages.error(request, f"Ocurrio un error: {formDepartamentos.errors}")             
            
            return render(request, "superadmin/gestionDepartamentos.html", {"allDepartamentos": departamentos,"form": formDepartamentos,'abrir_modal_por_error': True , "filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
    return render(request, "superadmin/gestionDepartamentos.html", {"allDepartamentos": departamentos,"form": formDepartamentos,"filtro":filtro,"cantidad_registros_base":qs_base.count()})


@superadmin_required
@login_required
def gestionDeEspecialidades(request):
    formEspecialidades = FormEspecialidades()
    
    qs_base = Especialidades.objects.all()
    filtro = EspecialidadesFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    especialidades = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_especialidades.html", {"allEspecialidades": especialidades,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
        id = request.GET.get('id')
        if id:
            especialidad = get_object_or_404(Especialidades, id=id)
            data = {
                "id": especialidad.id,
                "nombre_especialidad": especialidad.nombre_especialidad,
                "permite_turno": especialidad.permite_turno,
                "descripcion": especialidad.descripcion,
                "capacidad_diaria": especialidad.capacidad_diaria,
                "departamento": especialidad.departamento.id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

    if request.method == "POST":
        id_especialidad = request.POST.get('id_especialidad')
        mensaje = ""
        if id_especialidad:
            especialidad = get_object_or_404(Especialidades, id=id_especialidad)
            formEspecialidades = FormEspecialidades(request.POST, instance=especialidad)
            mensaje="Se editó correctamente la especialidad."
        else:
            formEspecialidades = FormEspecialidades(request.POST)
            mensaje="Se añadió correctamente la especialidad."

        if formEspecialidades.is_valid():
            formEspecialidades.save()
            messages.succes(request,mensaje)
            return redirect("gestionDeEspecialidades")  
        else:
            messages.error(request,"Ocurrió un error. Intentelo de nuevo.")            
            return render(request, "superadmin/gestionEspecialidades.html", {"allEspecialidades": especialidades,"form": formEspecialidades,'abrir_modal_por_error': True,"filtro":filtro,"cantidad_registros_base":qs_base.count()  })
        
    return render(request, "superadmin/gestionEspecialidades.html", {"allEspecialidades": especialidades,"form": formEspecialidades,"filtro":filtro,"cantidad_registros_base":qs_base.count()  })


@superadmin_required
@login_required
def gestionDeServiciosDiagnostico(request):
    formServicios = FormServiciosDiagnostico()
    
    qs_base = ServicioDiagnostico.objects.all()
    filtro = ServiciosFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    servicios = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_serviciosDiagnostico.html", {"allServicios": servicios,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
        id = request.GET.get('id')
        if id:
            servicio = get_object_or_404(ServicioDiagnostico, id=id)
            data = {
                "id_servicio": servicio.id,
                "nombre_servicio": servicio.nombre_servicio,
                "descripcion_servicio": servicio.descripcion,
                "departamento_servicio": servicio.departamento.id,
                "capacidad_diaria_servicio": servicio.capacidad_diaria,
                "lugar_servicio": [lugar.id for lugar in servicio.lugar.all()]            
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

    if request.method == "POST":
        id_servicio = request.POST.get('id_servicio')
        mensaje = ""
        if id_servicio:
            servicio = get_object_or_404(ServicioDiagnostico, id=id_servicio)
            formServicios = FormServiciosDiagnostico(request.POST, instance=servicio)
            mensaje = "Se editó correctamente el servicio"
        else:
            formServicios = FormServiciosDiagnostico(request.POST)
            mensaje = "Se añadió correctamente el servicio"
            
        if formServicios.is_valid():
            formServicios.save()
            messages.succes(request,mensaje)
            return redirect("gestionDeServiciosDiagnostico")  
        else:
            messages.error(request,"Ocurrió un error. Intentelo de nuevo")
            return render(request, "superadmin/gestionServiciosDiagnostico.html", {"allServicios": servicios,"form": formServicios,'abrir_modal_por_error': True, "filtro":filtro,"cantidad_registros_base":qs_base.count()  })

    return render(request, "superadmin/gestionServiciosDiagnostico.html", {"allServicios": servicios,"form": formServicios,"filtro":filtro,"cantidad_registros_base":qs_base.count()  })

@superadmin_required
@login_required
def gestionDeEstudiosDiagnostico(request):
    formEstudiosDiagnostico = FormEstudiosDiagnosticos()
    
    qs_base = EstudiosDiagnosticos.objects.all()
    filtro = EstudiosFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    estudios = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_estudios.html", {"allEstudios": estudios,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
        id = request.GET.get('id')
        if id:
            estudio = get_object_or_404(EstudiosDiagnosticos, id=id)
            data = {
                "id_estudio": estudio.id,
                "nombre_estudio": estudio.nombre_estudio,
                "servicio_estudio": estudio.servicio_diagnostico.id,
                "especialidad_estudio": [especialidad.id for especialidad in estudio.especialidad.all()],           
                "tipo_resultado": estudio.tipo_resultado
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

    if request.method == "POST":
        id_estudio = request.POST.get('id_estudio')
        mensaje = ""
        if id_estudio:
            estudio = get_object_or_404(EstudiosDiagnosticos, id=id_estudio)
            formEstudiosDiagnostico = FormEstudiosDiagnosticos(request.POST, instance=estudio)
            mensaje="Se editó correctamente el estudio."
        else:
            formEstudiosDiagnostico = FormEstudiosDiagnosticos(request.POST)
            mensaje="Se añadió correctamente el estudio."
            

        if formEstudiosDiagnostico.is_valid():
            formEstudiosDiagnostico.save()
            messages.succes(request,mensaje)
            return redirect("gestionDeEstudiosDiagnostico")  
        else:
            messages.error(request,"Ocurrió un error. Intentelo de nuevo.")
            return render(request, "superadmin/estudios/gestionEstudiosDiagnosticos.html", {"allEstudios": estudios,"form": formEstudiosDiagnostico,'abrir_modal_por_error': True,"filtro":filtro,"cantidad_registros_base":qs_base.count()  })

    return render(request, "superadmin/estudios/gestionEstudiosDiagnosticos.html", {"allEstudios": estudios,"form": formEstudiosDiagnostico,"filtro":filtro,"cantidad_registros_base":qs_base.count()  })

@superadmin_required
@login_required
def gestionDeLugares(request):
    formLugar = FormLugar()
    
    qs_base = Lugar.objects.all()
    filtro = LugarFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    lugares = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_lugares.html", {"allLugares": lugares,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
        id = request.GET.get('id')
        if id:
            lugar = get_object_or_404(Lugar, id=id)
            data = {
                "id_lugar": lugar.id,
                "nombre_lugar": lugar.nombre,
                "tipo_lugar": lugar.tipo,
                "piso_lugar": lugar.piso,
                "sala_lugar": lugar.sala,
                "abreviacion_lugar": lugar.abreviacion,
                "capacidad_lugar": lugar.capacidad,
                "departamento_lugar": lugar.departamento.id,
                "unidad_lugar": getattr(lugar.unidad, 'id', None),
                "descripcion_lugar": lugar.descripcion,
                "isCritico_lugar": lugar.es_critico,
                "isActivo_lugar": lugar.activo,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

    if request.method == "POST":
        id_lugar = request.POST.get('id_lugar')
        mensaje =""
        if id_lugar:
            lugar = get_object_or_404(Lugar, id=id_lugar)
            formLugar = FormLugar(request.POST, instance=lugar)
            mensaje ="Se editó correctamente el lugar."
        else:
            formLugar = FormLugar(request.POST)
            mensaje ="Se añadió correctamente el lugar."
            

        if formLugar.is_valid():
            formLugar.save()
            messages.succes(request,mensaje)
            return redirect("gestionDeLugares")  
        else:
            messages.error(request,f"Ocurrió un error. Intenelo de nuevo. ({formLugar.errors})")
            return render(request, "superadmin/gestionLugares.html", {"allLugares": lugares,"form": formLugar,"filtro":filtro,'abrir_modal_por_error': True,"cantidad_registros_base":qs_base.count()  })

    return render(request, "superadmin/gestionLugares.html", {"allLugares": lugares,"form": formLugar, "filtro":filtro,"cantidad_registros_base":qs_base.count()  })

@superadmin_required
@login_required
def gestionDePlantillasEstudios(request):
    formPlantillaEstudio = FormPlantillaEstudio()
    
    qs_base = PlantillaEstudio.objects.all()
    filtro = PlantillaEstudioFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    plantillas = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_plantillaEstudios.html", {"allPlantillas": plantillas,"filtro":filtro,"cantidad_registros_base":qs_base.count()})

        id = request.GET.get('id')
        if id:
            plantilla = get_object_or_404(PlantillaEstudio, id=id)
            data = {
                "id_plantilla": plantilla.id,
                "estudio_plantilla": plantilla.estudio.id,
                "estructura_estudio": plantilla.estructura
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

    if request.method == "POST":
        id_plantilla = request.POST.get('id_plantilla')
        mensaje = ""
        if id_plantilla:
            plantilla = get_object_or_404(PlantillaEstudio, id=id_plantilla)
            formPlantillaEstudio = FormPlantillaEstudio(request.POST, instance=plantilla)
            mensaje = "Se editó correctamente la plantilla."
        else:
            formPlantillaEstudio = FormPlantillaEstudio(request.POST)
            mensaje = "Se añadió correctamente la plantilla."
            

        if formPlantillaEstudio.is_valid():
            formPlantillaEstudio.save()
            messages.succes(request,mensaje)
            return redirect("gestionDePlantillasEstudios")  
        else:
            messages.error(request,"Ocurrió un error. Intentelo de nuevo.")            
            return render(request, "superadmin/estudios/gestionPlantillaEstudios.html", {"allPlantillas": plantillas,"form": formPlantillaEstudio,'abrir_modal_por_error': True,"filtro":filtro,"cantidad_registros_base":qs_base.count()  })

    return render(request, "superadmin/estudios/gestionPlantillaEstudios.html", {"allPlantillas": plantillas,"form": formPlantillaEstudio,"filtro":filtro,"cantidad_registros_base":qs_base.count()  })

@superadmin_required
@login_required
def gestionDeRoles(request):
    tiposUsuario = TiposUsuarios.objects.all()
    formTipoUsuario = FormTiposUsuarios()
    formRolesProfesionales = FormRolesProfesionales()
    
    qs_base = RolesProfesionales.objects.all()
    filtro = RolesProfesionalesFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    rolesProfesionales = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_rolesProfesionales.html", {"allRolesProfesionales": rolesProfesionales,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_rol_profesional = request.GET.get('id_rol_profesional')
        id_tipo_usuario = request.GET.get('id_tipo_usuario')
        if id_rol_profesional:
            rol_profesional = get_object_or_404(RolesProfesionales, id=id_rol_profesional)
            data = {
                "id_rol_profesional": rol_profesional.id,
                "nombre_rol_profesional": rol_profesional.nombre_rol_profesional,
                "tipo_usuario": rol_profesional.tipoUsuario.id,
                "id_especialidad": getattr(rol_profesional.especialidad, 'id', None),
                "id_servicio": getattr(rol_profesional.servicio_diagnostico, 'id', None),
                "id_departamento": getattr(rol_profesional.departamento, 'id', None),
                "nombre_especialidad": getattr(rol_profesional.especialidad, 'nombre_especialidad', None), # Este solo lo vamos a utilizar en la vista de asignar rol profesional
                "nombre_servicio": getattr(rol_profesional.servicio_diagnostico, 'nombre_servicio', None), # Este solo lo vamos a utilizar en la vista de asignar rol profesional
                "nombre_departamento": getattr(rol_profesional.departamento, 'nombre_departamento', None) # Este solo lo vamos a utilizar en la vista de asignar rol profesional
            }
            return JsonResponse(data)
        elif id_tipo_usuario :
            tipo_usuario = get_object_or_404(TiposUsuarios, id=id_tipo_usuario)
            data = {
                "id_tipo_usuario": tipo_usuario.id,
                "nombre_tipo_usuario": tipo_usuario.nombre_tipoUsuario
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

    if request.method == "POST":
        tipo_form = request.POST.get('tipo-form')
        if tipo_form == "FormRolProfesional":
            id_rol_profesional = request.POST.get('id_rol_profesional')
            mensaje= ""
            if id_rol_profesional:
                rol_profesional = get_object_or_404(RolesProfesionales, id=id_rol_profesional)
                formRolesProfesionales = FormRolesProfesionales(request.POST, instance=rol_profesional)
                title = "Editar rol profesional"
                mensaje = "Se editó correctamente el rol profesional."
            else:
                formRolesProfesionales = FormRolesProfesionales(request.POST)
                mensaje = "Se añadió correctamente el rol profesional."
                
                title = "Nuevo rol profesional"

            if formRolesProfesionales.is_valid():
                formRolesProfesionales.save()
                messages.succes(request,mensaje)
                return redirect("gestionDeRoles")
            else:
                messages.error(request,"Ocurrió un error. Intentelo de nuevo.")
                return render(request, "superadmin/gestionRoles.html", {
                    "allTiposUsuarios": tiposUsuario,
                    "allRolesProfesionales": rolesProfesionales,
                    "formTipoUsuarios": formTipoUsuario,
                    "formRolesProfesionales": formRolesProfesionales,
                    'abrir_modal_rol_profesional_por_error': True,
                    'title_modal': title,
                    "filtro":filtro,
                    "cantidad_registros_base":qs_base.count()
                })   
            
        elif tipo_form == "FormTipoUsuario":
            id_tipo_usuario = request.POST.get('id_tipo_usuario')
            mensaje= ""            
            if id_tipo_usuario:
                tipo_usuario = get_object_or_404(TiposUsuarios, id=id_tipo_usuario)
                formTipoUsuario = FormTiposUsuarios(request.POST, instance=tipo_usuario)
                title = "Editar tipo de usuario"
                mensaje = "Se editó correctamente el tipo de usuario."
                
            else:
                formTipoUsuario = FormTiposUsuarios(request.POST)
                title = "Nuevo tipo de usuario"
                mensaje = "Se añadió correctamente el tipo de usuario."
                
            
            if formTipoUsuario.is_valid():
                formTipoUsuario.save()
                messages.succes(request,mensaje)                
                return redirect("gestionDeRoles")
            else:
                messages.error(request,"Ocurrió un error. Intentelo de nuevo.")                
                return render(request, "superadmin/gestionRoles.html", {
                    "allTiposUsuarios": tiposUsuario,
                    "allRolesProfesionales": rolesProfesionales,
                    "formTipoUsuarios": formTipoUsuario,
                    "formRolesProfesionales": formRolesProfesionales,
                    'abrir_modal_tipo_usuario_por_error': True,
                    'title_modal': title,
                    "filtro":filtro,
                    "cantidad_registros_base":qs_base.count()
                })
        else:
            response = render(request, "403.html", {
                "mensaje": "Este formulario no existe ."
            })
            response.status_code = 403
            return response                    
                
    return render(request, "superadmin/gestionRoles.html", {
        "allTiposUsuarios": tiposUsuario,
        "allRolesProfesionales": rolesProfesionales,
        "formTipoUsuarios": formTipoUsuario,
        "formRolesProfesionales": formRolesProfesionales,
        "filtro":filtro,"cantidad_registros_base":qs_base.count()
    })   

@superadmin_required
@login_required
def listaPacientes(request):   
    qs_base = Paciente.objects.all()
    filtro = PacienteFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    pacientes = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"superadmin/tablasDinamicas/_tabla_pacientes.html", {"allPacientes": pacientes,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
    return render(request, "superadmin/listaPacientes/listaPacientes.html", {"allPacientes":pacientes,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@superadmin_required
@login_required
def turnosPaciente(request, id):
    paciente = Paciente.objects.get(id=id)
    turnosDelPaciente = Turno.objects.filter(paciente_id=id)
    turnosEstudiosDelPaciente = TurnoEstudio.objects.filter(orden__consulta__turno__paciente_id=id)
    return render(request, "superadmin/listaPacientes/turnosPaciente.html", {"turnosDelPaciente":turnosDelPaciente,"turnosEstudiosDelPaciente": turnosEstudiosDelPaciente, "paciente":paciente}) 
