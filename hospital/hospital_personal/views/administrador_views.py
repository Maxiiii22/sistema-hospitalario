from collections import defaultdict
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required 
from controlUsuario.models import Usuario,RolesProfesionales
from controlUsuario.forms import FormularioRegistroDePersonal
from hospital_personal.models import UsuarioLugarTrabajoAsignado,UsuarioRolProfesionalAsignado,Especialidades,Turno,Consultas,TurnoEstudio,SolicitudReactivacion
from hospital_personal.filters import MedicosConCitasFilter,UsuariosNoAdministracionFilter, MedicosFilter, SolicitudesReactivacionFilter
from django.db.models import Q
from django.utils import timezone
from hospital_pacientes.utils import obtener_disponibilidad
from django.db import transaction
from datetime import datetime
from django.db.models import Count
from datetime import datetime, timedelta
import calendar
from django.db.models import Min
from controlUsuario.decorators import administrador_required

@administrador_required
@login_required
def gestionDelPersonal(request):
    qs_base = Usuario.objects.exclude(Q(persona__is_active=False) | Q(tipoUsuario_id__in=[1,2]))
    filtro = UsuariosNoAdministracionFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    personal = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"administrador/gestionPersonal/tablasDinamicas/_tabla_personal.html", {"allPersonal": personal,"filtro":filtro,"cantidad_registros_base":qs_base.count()})   
    
    return render(request, "administrador/gestionPersonal/gestionPersonal.html", {"allPersonal":personal,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@administrador_required
@login_required
def detalle_usuario(request,id_usuario):
    if not Usuario.objects.filter(pk=id_usuario,tipoUsuario__in=[3,4,5,6,7,8]).exists():
        response = render(request, "403.html", {
            "mensaje": "Este usuario no existe o no es accesible para ti"
        })
        response.status_code = 403
        return response       
    
    usuario = Usuario.objects.get(pk=id_usuario)

    
    rolesProfesionales = UsuarioRolProfesionalAsignado.objects.filter(usuario=usuario)
    asignacionesDeLugarDeTrabajo = UsuarioLugarTrabajoAsignado.objects.filter(usuario=usuario).order_by('jornada')

    departamentos_con_jornadas = defaultdict(list)
    for asignacion in asignacionesDeLugarDeTrabajo:
        especialidad_o_servicio = (
            getattr(asignacion.rolProfesionalAsignado.rol_profesional.especialidad, 'nombre_especialidad', None) or getattr(asignacion.rolProfesionalAsignado.rol_profesional.servicio_diagnostico, 'nombre_servicio', None)
        )  
        rolProfesional = None
        if asignacion.rolProfesionalAsignado.rol_profesional.tipoUsuario.id == 7: # Si es jefe de enfermeria
            rolProfesional = f"{asignacion.rolProfesionalAsignado.rol_profesional.tipoUsuario} ({asignacion.rolProfesionalAsignado.rol_profesional.nombre_rol_profesional})"
        else:
            rolProfesional = asignacion.rolProfesionalAsignado.rol_profesional.nombre_rol_profesional   
        
        departamentos_con_jornadas[asignacion.lugar.departamento].append({
            "id": f"{asignacion.id}",
            "info": f"Los días <strong>{asignacion.jornada.get_dia_display()}</strong> en el turno: <strong>{asignacion.jornada.get_turno_display()}</strong> trabaja en el <strong>{asignacion.lugar.nombre} ({asignacion.lugar.abreviacion})</strong> como <strong>{rolProfesional}"
                + (f" (En {especialidad_o_servicio})" if especialidad_o_servicio else "")+ "</strong>"
        })
        
    
    departamentos_con_jornadas = dict(departamentos_con_jornadas)
    formUsuario = FormularioRegistroDePersonal(persona_instance=usuario.persona,usuario_instance=usuario,user=request.user)
    
    if request.method == 'POST':
        tipo_form = request.POST.get("tipo_form")
        
        if tipo_form == "form_editarPersonal":
            formUsuario = FormularioRegistroDePersonal(
                request.POST,
                persona_instance=usuario.persona,
                usuario_instance=usuario,
                user=request.user  # Esto es para comprobar que el usuario es un Administrador
            )
            if formUsuario.is_valid():
                usuario_guardado = formUsuario.save(commit=True)  
                messages.success(request,"Se editó correctamente.")
                return redirect('detalle_usuario', id=usuario_guardado.id) 
            else:
                messages.error(request,"Ocurrió un error. Intentelo de nuevo.")
            

    return render(request, "administrador/gestionPersonal/detallesUsuario.html",{"usuario":usuario,"rolesProfesionales":rolesProfesionales,"departamentos_con_jornadas": departamentos_con_jornadas,"formUsuario":formUsuario})

@administrador_required
@login_required
def gestionAgendas(request):
    hoy = timezone.localtime().date()
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
    asignacionTrabajo = request.user.usuario.UsuariosAsignadosAEsteLugar.all()
    jornada = None
    for asignacion in asignacionTrabajo:
        if asignacion.jornada.dia == dia_semana:
            jornada = asignacion.jornada
            break    
    
    qs_base = Usuario.objects.filter(tipoUsuario_id=3, persona__is_active=True)    
    filtro = MedicosConCitasFilter(request.GET, queryset=qs_base,jornada=jornada, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    medicos = filtro.qs
        
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"administrador/gestionAgendas/tablasDinamicas/_tabla_medicos.html", {"allMedicos": medicos,"filtro":filtro,"jornada":jornada,"cantidad_registros_base":qs_base.count()})   
    
    return render(request, "administrador/gestionAgendas/gestionAgendas.html", {"allMedicos":medicos,"filtro":filtro,"jornada":jornada,"cantidad_registros_base":qs_base.count()}) 

@administrador_required
@login_required
def agendaMedico(request,id_medico):
    if not Usuario.objects.filter(pk=id_medico,tipoUsuario_id=3,persona__is_active=True).exists():
        response = render(request, "403.html", {
            "mensaje": "Este usuario no existe o no es accesible para ti"
        })
        response.status_code = 403
        return response       
    
    medico = Usuario.objects.get(pk=id_medico)
    
    asignacionMedico = medico.get_asignacionActual()
    
    rolProfesional = RolesProfesionales.objects.get(pk=asignacionMedico["asignacionActualId"])
    especialidad = Especialidades.objects.get(pk=rolProfesional.especialidad.id)
    
    turnos_hoy = []
    turnos_otros_dias = []
    if especialidad:
        hoy = timezone.localtime().date() 
        turnos = Turno.objects.filter(profesional=medico, fecha_turno__gte=hoy,especialidad=especialidad ).order_by("fecha_turno") # fecha_turno__gte=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea hoy o en el futuro
        
        for turno in turnos:
            if turno.fecha_turno == hoy:
                turnos_hoy.append(turno)
            else:
                turnos_otros_dias.append(turno)
    
    
    if request.method == "GET" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        id_turno = request.GET.get("id_turno")
        turno = get_object_or_404(Turno, id=id_turno)
        
        if id_turno:
            disponibilidad = obtener_disponibilidad(turno.profesional_id,turno.horario_turno,turno.especialidad.id,turno.paciente.id)
            dias_disponibles = [{
                "profesional": turno.profesional_id,
                "disponibilidad": disponibilidad
            }]
            return JsonResponse({
                "id": id_turno,
                "dias_disponibles": dias_disponibles
            })
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)   
    
    
    
    if request.method == "POST":
        tipo_form = request.POST.get("tipo_form")
        
        if tipo_form == "formReprogramarCita":         
            id_turno = request.POST.get("id_turno")

            if not Turno.objects.filter(pk=id_turno,profesional=medico,estado="pendiente").exists():
                response = render(request, "403.html", {
                    "mensaje": "Este turno no existe o ya fue atendido"
                })
                response.status_code = 403
                return response                  
            
            turno = get_object_or_404(Turno, pk=id_turno)
        
            hoy = timezone.localtime()
            fecha_seleccionada = request.POST.get("fecha_seleccionada") 
            fecha_seleccionada = datetime.strptime(fecha_seleccionada, "%Y-%m-%d").strftime("%Y-%m-%d")
            
        
            # Validar fecha disponible:
            disponibilidad = obtener_disponibilidad(turno.profesional_id,turno.horario_turno,turno.especialidad.id,turno.paciente.id)
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
                    messages.success(request, "Se reprogramó correctamente el turno.")
                    return redirect("administrador-agenda-medico", id_medico=medico.id)                        
            except Exception as e:
                messages.error(request, f"Ocurrió un error al reprogramar el turno: {str(e)}")    
                
        elif tipo_form == "formCancelarCita":         
            id_turno = request.POST.get("id_turno")

            if not Turno.objects.filter(pk=id_turno,profesional=medico,estado="pendiente").exists():
                response = render(request, "403.html", {
                    "mensaje": "Este turno no existe o ya fue atendido"
                })
                response.status_code = 403
                return response                  
            
            turno = get_object_or_404(Turno, pk=id_turno)
            
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    turno.estado = "cancelado"
                    turno.asistio = False
                    turno.save()
                    messages.success(request, "Se canceló correctamente el turno.")
                    return redirect("administrador-agenda-medico", id_medico=medico.id)                        
            except Exception as e:
                messages.error(request, f"Ocurrió un error al cancelar el turno: {str(e)}")                          
            
        else:
            response = render(request, "403.html", {
                "mensaje": "Formulario no encontrado"
            })
            response.status_code = 403
            return response               

            
    return render(request, "administrador/gestionAgendas/agendaMedico.html", {"medico":medico,"turnos_hoy": turnos_hoy,"turnos_otros_dias": turnos_otros_dias,"especialidad":especialidad}) 

@administrador_required
@login_required
def reportes(request, anio=None, mes=None, dia=None):
    anio = request.GET.get("anio", anio)
    mes = request.GET.get("mes", mes)
    dia = request.GET.get("dia", dia)

    now = timezone.localtime(timezone.now())

    tipo = request.GET.get("tipo","diario") 

    try:
        anio = int(anio)
        if anio < 2000 or anio > 2100:
            anio = now.year
    except (TypeError, ValueError):
        anio = now.year

    try:
        mes = int(mes)
        if mes < 1 or mes > 12:
            mes = now.month
    except (TypeError, ValueError):
        mes = now.month

    if tipo == "diario":
        try:
            dia = int(dia)
            ultimo_dia = calendar.monthrange(anio, mes)[1]
            if dia < 1 or dia > ultimo_dia:
                dia = now.day
        except (TypeError, ValueError):
            dia = now.day
    else:
        dia = 1  # default para mensual


    if tipo == "diario":
        inicio = timezone.make_aware(datetime(anio, mes, dia))
        fin = inicio + timedelta(days=1)
        tipo_reporte = "diario"
    else:  
        inicio = timezone.make_aware(datetime(anio, mes, 1))
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fin = timezone.make_aware(datetime(anio, mes, ultimo_dia, 23, 59, 59)) + timedelta(seconds=1)
        tipo_reporte = "mensual"
    

    def calcular_estadisticas(inicio, fin):
        consultas = Consultas.objects.filter(fecha__gte=inicio, fecha__lt=fin)
        total = consultas.count()
        totalAtendidas = consultas.filter(turno__estado="atendido").count()
        detalle = consultas.values("turno__especialidad__nombre_especialidad").annotate(total=Count("id"))
        nuevos_pacientes = (Consultas.objects.values("turno__paciente_id")
                            .annotate(primera_fecha=Min("fecha"))
                            .filter(primera_fecha__gte=inicio, primera_fecha__lt=fin)
                            .count())
        cancelaron = consultas.filter(turno__estado="cancelado").count()
        noAsistieron = consultas.filter(turno__asistio=False, turno__estado="noAsistio").count()
        return {
            "total": total,
            "totalAtendidas": totalAtendidas,
            "detalle": detalle,
            "nuevos_pacientes": nuevos_pacientes,
            "cancelaron": cancelaron,
            "noAsistieron": noAsistieron,
        }

    if tipo_reporte == "diario":
        diario = calcular_estadisticas(inicio, fin)
        mensual = {}
    else:
        diario = {}
        mensual = calcular_estadisticas(inicio, fin)
    

    contexto = {
        "diario": diario,
        "mensual": mensual,
        "fecha_inicio": inicio,
        "fecha_fin": fin - timedelta(seconds=1),
        "tipo_reporte": tipo_reporte,
    }

    return render(request, "administrador/reportes-y-estadisticas/reportes.html", contexto)

@administrador_required
@login_required
def reportes_servicios(request, anio=None, mes=None, dia=None):
    anio = request.GET.get("anio", anio)
    mes = request.GET.get("mes", mes)
    dia = request.GET.get("dia", dia)

    now = timezone.localtime(timezone.now())

    tipo = request.GET.get("tipo","diario") 

    try:
        anio = int(anio)
        if anio < 2000 or anio > 2100:
            anio = now.year
    except (TypeError, ValueError):
        anio = now.year

    try:
        mes = int(mes)
        if mes < 1 or mes > 12:
            mes = now.month
    except (TypeError, ValueError):
        mes = now.month

    if tipo == "diario":
        try:
            dia = int(dia)
            ultimo_dia = calendar.monthrange(anio, mes)[1]
            if dia < 1 or dia > ultimo_dia:
                dia = now.day
        except (TypeError, ValueError):
            dia = now.day
    else:
        dia = 1  # default para mensual


    if tipo == "diario":
        inicio = timezone.make_aware(datetime(anio, mes, dia))
        fin = inicio + timedelta(days=1)
        tipo_reporte = "diario"
    else:  
        inicio = timezone.make_aware(datetime(anio, mes, 1))
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fin = timezone.make_aware(datetime(anio, mes, ultimo_dia, 23, 59, 59)) + timedelta(seconds=1)
        tipo_reporte = "mensual"
    

    def calcular_estadisticas(inicio, fin):
        estudiosSolicitados = TurnoEstudio.objects.filter(fecha_turno__gte=inicio, fecha_turno__lt=fin)
        totalSolicitados = estudiosSolicitados.count()
        totalRealizados = estudiosSolicitados.exclude(estado__in=["pendiente","cancelado","noAsistio"]).count()
        detalle = estudiosSolicitados.values("orden__tipo_estudio__nombre_estudio").annotate(total=Count("id"))
        nuevos_pacientes = (TurnoEstudio.objects.values("orden__paciente_id")
                            .annotate(primera_fecha=Min("fecha_turno"))
                            .filter(primera_fecha__gte=inicio, primera_fecha__lt=fin)
                            .count())
        cancelaron = estudiosSolicitados.filter(estado="cancelado").count()
        noAsistieron = estudiosSolicitados.filter(asistio=False, estado="noAsistio").count()
        return {
            "totalSolicitados": totalSolicitados,
            "totalRealizados": totalRealizados,
            "detalle": detalle,
            "nuevos_pacientes": nuevos_pacientes,
            "cancelaron": cancelaron,
            "noAsistieron": noAsistieron,
        }

    if tipo_reporte == "diario":
        diario = calcular_estadisticas(inicio, fin)
        mensual = {}
    else:
        diario = {}
        mensual = calcular_estadisticas(inicio, fin)
    

    contexto = {
        "diario": diario,
        "mensual": mensual,
        "fecha_inicio": inicio,
        "fecha_fin": fin - timedelta(seconds=1),
        "tipo_reporte": tipo_reporte,
    }

    return render(request, "administrador/reportes-y-estadisticas/reportes_servicios.html", contexto)

@administrador_required
@login_required
def listaMedicos(request):  
    qs_base = Usuario.objects.filter(tipoUsuario_id=3,persona__is_active=True)
    filtro = MedicosFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    medicos = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"administrador/listaMedicos/tablasDinamicas/_tabla_medicos.html", {"allMedicos": medicos,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
    return render(request, "administrador/listaMedicos/listaMedicos.html", {"allMedicos":medicos,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@administrador_required
@login_required
def productividadMedica(request,id_medico, anio=None, mes=None, dia=None, especialidad=None):
    if not Usuario.objects.filter(pk=id_medico,tipoUsuario_id=3,persona__is_active=True).exists():
        response = render(request, "403.html", {
            "mensaje": "Este médico no existe"
        })
        response.status_code = 403
        return response                  
            
    medico = get_object_or_404(Usuario, pk=id_medico)
    
    roles = medico.rolesProfesionalesUsuario.all()
    if not roles.exists():
        response = render(request, "403.html", {
            "mensaje": "Este médico no tiene asignaciones registradas. Por favor, contacte al Administrador del Sistema para resolver la situación."
        })
        response.status_code = 403
        return response

    especialidades = [rol.rol_profesional.especialidad for rol in roles]              

    
    anio = request.GET.get("anio", anio)
    mes = request.GET.get("mes", mes)
    dia = request.GET.get("dia", dia)
    especialidad = request.GET.get("especialidad", especialidad)
    
    if especialidad is None or not especialidad :
        primera_especialidad = especialidades[0]
        especialidad = primera_especialidad.id
    
    if not UsuarioRolProfesionalAsignado.objects.filter(usuario=medico,rol_profesional__especialidad_id=especialidad).exists():
        response = render(request, "403.html", {
            "mensaje": "Este médico no tiene esa especialidad asignada"
        })
        response.status_code = 403
        return response    
    

    now = timezone.localtime(timezone.now())

    tipo = request.GET.get("tipo","diario") 

    try:
        anio = int(anio)
        if anio < 2000 or anio > 2100:
            anio = now.year
    except (TypeError, ValueError):
        anio = now.year

    try:
        mes = int(mes)
        if mes < 1 or mes > 12:
            mes = now.month
    except (TypeError, ValueError):
        mes = now.month

    if tipo == "diario":
        try:
            dia = int(dia)
            ultimo_dia = calendar.monthrange(anio, mes)[1]
            if dia < 1 or dia > ultimo_dia:
                dia = now.day
        except (TypeError, ValueError):
            dia = now.day
    else:
        dia = 1  # default para mensual


    if tipo == "diario":
        inicio = timezone.make_aware(datetime(anio, mes, dia))
        fin = inicio + timedelta(days=1)
        tipo_reporte = "diario"
    else:  
        inicio = timezone.make_aware(datetime(anio, mes, 1))
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fin = timezone.make_aware(datetime(anio, mes, ultimo_dia, 23, 59, 59)) + timedelta(seconds=1)
        tipo_reporte = "mensual"
    

    def calcular_estadisticas(inicio, fin, especialidad):
        consultas = Consultas.objects.filter(fecha__gte=inicio, fecha__lt=fin, turno__profesional=medico, turno__especialidad_id=especialidad)
        total = consultas.count()
        totalAtendidas = consultas.filter(turno__estado="atendido").count()
        cancelaron = consultas.filter(turno__estado="cancelado").count()
        noAsistieron = consultas.filter(turno__asistio=False, turno__estado="noAsistio").count()
        detalle = consultas.values("turno__especialidad__nombre_especialidad").annotate(total=Count("id"))
        nuevos_pacientes = (Consultas.objects.values("turno__paciente_id")
                            .annotate(primera_fecha=Min("fecha"))
                            .filter(primera_fecha__gte=inicio, primera_fecha__lt=fin,turno__profesional=medico,turno__especialidad_id=especialidad)
                            .count())
        return {
            "total": total,
            "totalAtendidas": totalAtendidas,
            "detalle": detalle,
            "nuevos_pacientes": nuevos_pacientes,
            "cancelaron": cancelaron,
            "noAsistieron": noAsistieron,
        }

    if tipo_reporte == "diario":
        diario = calcular_estadisticas(inicio, fin, especialidad)
        mensual = {}
    else:
        diario = {}
        mensual = calcular_estadisticas(inicio, fin, especialidad)
    

    contexto = {
        "medico":medico,
        "especialidadesDelMedico":especialidades,                
        "diario": diario,
        "mensual": mensual,
        "fecha_inicio": inicio,
        "fecha_fin": fin - timedelta(seconds=1),
        "tipo_reporte": tipo_reporte
    }

    return render(request, "administrador/listaMedicos/productividadMedica.html",contexto)


@administrador_required
@login_required
def solicitudesReactivacion(request):  
    verificarSolicitudes = SolicitudReactivacion.objects.all()
    for solicitud in verificarSolicitudes:
        solicitud.marcar_vencida_si_corresponde()
        
    mostrar_todas = request.GET.get("todas_las_solicitudes")

    if mostrar_todas:
        qs_base = SolicitudReactivacion.objects.all()
    else:
        qs_base = SolicitudReactivacion.objects.filter(estado="pendiente")

    filtro = SolicitudesReactivacionFilter(
        request.GET or None,
        queryset=qs_base
    )
    solicitudes = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"administrador/listaSolicitudes/tablasDinamicas/_tabla_solicitudes.html", {"solicitudes": solicitudes,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
        id_solicitud = request.GET.get('id_solicitud')
        if id_solicitud:
            solicitud = get_object_or_404(SolicitudReactivacion, pk=id_solicitud)
            paciente = {
                "dni": solicitud.paciente.persona.dni,
                "nombre":solicitud.paciente.persona.first_name,
                "apellido":solicitud.paciente.persona.last_name,
                "fecha_nacimiento":solicitud.paciente.persona.fecha_nacimiento.strftime("%d-%m-%Y"),
                "email":solicitud.paciente.persona.login_id,
                "telefono":solicitud.paciente.persona.telefono,
                "numero_paciente":solicitud.paciente.numero_paciente
            }
            data = {
                "paciente": paciente,
                "id_solicitud": solicitud.id,
                "dni": solicitud.dni,
                "nombre": solicitud.first_name,
                "apellido": solicitud.last_name,
                "nacimiento": solicitud.fecha_nacimiento.strftime("%d-%m-%Y"),
                "email": solicitud.login_id if solicitud.login_id else "No completo este campo",
                "telefono": solicitud.telefono if solicitud.telefono else "No completo este campo",
                "numero_paciente": solicitud.numero_paciente if solicitud.numero_paciente else "No completo este campo",
                "observaciones": solicitud.observaciones if solicitud.observaciones else "No completo este campo",
                "estado": solicitud.estado
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)     
    
    if request.method == "POST":
        accion = request.POST.get("accion")
        id_solicitud = request.POST.get("id_solicitud")
        
        if id_solicitud:
            try:
                id_solicitud = int(id_solicitud)
            except (TypeError, ValueError):
                messages.error(request,"El campo tiene que ser un entero.")
                return redirect("administrador-solicitudes-reactivacion")
        else:
            messages.error(request,"El campo no debe estar vacio.")
            return redirect("administrador-solicitudes-reactivacion")           
        
        try:
            solicitud = SolicitudReactivacion.objects.get(pk=id_solicitud)  
        except SolicitudReactivacion.DoesNotExist:
            messages.error(request, "No se encontró ningúna solicitud con los datos proporcionados.")
            return redirect("administrador-solicitudes-reactivacion")           

        if solicitud.estado != "pendiente":
            messages.error(request, "Esta solicitud ya fue respondida.")
            return redirect("administrador-solicitudes-reactivacion")           
        
        if accion == "aceptar":
            solicitud.estado = "aprobada"
        elif accion == "rechazar":
            solicitud.estado = "rechazada"
        else:
            response = render(request, "403.html", {
                "mensaje": "No tienes acceso a esta pagina"
            })
            response.status_code = 403
            return response 
        
        solicitud.save()
        messages.success(request,f"La solicitud fue {solicitud.estado} correctamente.")
        return redirect("administrador-solicitudes-reactivacion")           
        
    return render(request, "administrador/listaSolicitudes/listaSolicitudes.html", {"solicitudes":solicitudes,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 