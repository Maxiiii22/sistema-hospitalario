from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import medico_required # En controlUsuario.decorators creamos decoradores personalizados que verifiquen si el usuario tiene el atributo de paciente o usuario, y redirigirlo a una página de acceso denegado si intenta acceder a una vista que no le corresponde.
from hospital_personal.models import Especialidades,Turno,Consultas,Medicaciones,OrdenEstudio,EstudiosDiagnosticos
from hospital_personal.forms import FormConsulta,MedicacionesFormSet,EstudiosFormSet
from hospital_personal.filters import ConsultasDelMedicoFilter
from hospital_pacientes.utils import obtener_disponibilidad
from django.contrib import messages
from django.db import transaction
from datetime import datetime


@medico_required
@login_required
def turnosProgramados(request):
    usuario_actual = request.user.usuario
    especialidad_id = request.session.get('especialidad_actual')
    hoy = timezone.localtime().date() 
    
    
    if especialidad_id:
        especialidad = Especialidades.objects.get(id=especialidad_id)
    else: 
        especialidad = False
        
    if request.method == "GET" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        id_turno = request.GET.get("id_turno")
        
        if not Turno.objects.filter(pk=id_turno,estado="pendiente").exists():
            response = render(request, "403.html", {
                "mensaje": "Este turno no existe o ya fue atendidó."
            })
            response.status_code = 403
            return response              
        
        turno = get_object_or_404(Turno, id=id_turno)
        
        # Verificar si el turno pertenece al profesional actual 
        if turno.profesional != usuario_actual:
            return HttpResponseForbidden(render(request, "403.html"))
        
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
        
    
    turnos_hoy = []
    turnos_otros_dias = []
    if especialidad:
        hoy = timezone.localtime().date() 
        turnos = Turno.objects.filter(profesional_id=request.user.usuario, fecha_turno__gte=hoy,especialidad=especialidad ).order_by("fecha_turno") # fecha_turno__gte=hoy: Este filtro asegura que solo se obtendrán los turnos cuya fecha sea hoy o en el futuro
        
        for turno in turnos:
            if turno.fecha_turno == hoy:
                turnos_hoy.append(turno)
            elif turno.fecha_turno < hoy and turno.estado in ["pendiente"]:
                turno.estado = "noAsistio"
                turno.save()
            else:
                turnos_otros_dias.append(turno)
        
    return render(request, "medico/turnos/turnosProgramados.html",{ "turnos_hoy": turnos_hoy,"turnos_otros_dias": turnos_otros_dias})

@medico_required
@login_required
def reprogramarTurno(request, turno_id):
    usuario_actual = request.user.usuario    
    
    if request.method == 'GET':
        return redirect("turnosProgramados")    
        
    if request.method == "POST":
        
        if not Turno.objects.filter(pk=turno_id,estado="pendiente").exists():
            response = render(request, "403.html", {
                "mensaje": "Este turno no existe o ya fue atendidó."
            })
            response.status_code = 403
            return response         
        
        turno = get_object_or_404(Turno, pk=turno_id)
        
        # Verificar si el turno pertenece al profesional actual 
        if turno.profesional != usuario_actual:
            response = render(request, "403.html", {
                "mensaje": "No puedes reprogramar este turno."
            })
            response.status_code = 403
            return response  
        
        hoy = timezone.localtime()
        fecha_seleccionada = request.POST.get("fecha_seleccionada") 
        fecha_seleccionada = datetime.strptime(fecha_seleccionada, "%Y-%m-%d").strftime("%Y-%m-%d")


        # Validar fecha disponible
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
                return redirect("turnosProgramados")                        
        except Exception as e:
            messages.error(request, f"Ocurrió un error al reprogramar el turno: {str(e)}")                
            return redirect("turnosProgramados")                        
    
    return HttpResponseForbidden(render(request, "403.html"))            



@medico_required
@login_required
def cancelarTurno(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)
    usuario_actual = request.user.usuario
    
    # Verificar si el turno pertenece al profesional actual
    if turno.profesional != usuario_actual:
        return HttpResponseForbidden(render(request, "403.html"))
    
    if request.method == 'GET':
        return redirect("turnosProgramados")
        
    if request.method == 'POST':
        try:
            with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                turno.estado = "cancelado"
                turno.asistio = False
                turno.save()
                messages.success(request, "Se canceló correctamente el turno.")
                return redirect("turnosProgramados")                        
        except Exception as e:
            messages.error(request, f"Ocurrió un error al cancelar el turno: {str(e)}")                
            return redirect("turnosProgramados")                        



@medico_required
@login_required
def registrarConsulta(request, id_turno):
    hoy = timezone.localtime().date() 
    turno = Turno.objects.get(id=id_turno)
    especialidad = turno.especialidad
    
    if turno.fecha_turno != hoy or turno.profesional != request.user.usuario: # Verificar si el turno es de hoy o si el profesional pedido para ese turno es el usuario actual
        return HttpResponseForbidden(render(request, "403.html"))
    
    if turno.consulta.exists(): # si ya hay una consulta asociada a ese turno
        response = render(request, "403.html", {
            "mensaje": "Ya hay una consulta asociada a este turno."
        })
        response.status_code = 403
        return response
        
    # historial de consultas del paciente en la misma especialidad
    consultas = Consultas.objects.filter(
        turno__paciente=turno.paciente,
        turno__especialidad=turno.especialidad
    ).prefetch_related('estudios', 'medicaciones').order_by('-fecha')[:10] 
    
    lista_estudios = EstudiosDiagnosticos.objects.filter(especialidad=especialidad)  # Estudios disponibles solo para esta especialidad
    
    form_consulta = FormConsulta(request.POST or None)
    
    estudios_formset = EstudiosFormSet(request.POST or None, queryset=OrdenEstudio.objects.none(), prefix='estudios')
    medicaciones_formset = MedicacionesFormSet(request.POST or None, queryset=Medicaciones.objects.none(), prefix='medicaciones')
    
    # Limitar SIEMPRE el queryset de tipo_estudio
    for form in estudios_formset.forms:
        form.fields['tipo_estudio'].queryset = lista_estudios
        
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        idOrden = request.GET.get('idOrden')
        idMedicamento = request.GET.get('idMedicamento')
        if idOrden:
            orden = get_object_or_404(OrdenEstudio, pk=idOrden)
            data = {
                "idConsulta": orden.consulta.id,
                "id_orden": orden.id,
                "tipo_estudio": orden.tipo_estudio.nombre_estudio,
                "motivo": orden.motivo_estudio,
                "indicaciones": orden.indicaciones,
                "estado": orden.estado_detallado,
                "fecha_solicitud": orden.fecha_solicitud.date(),
                "profesional": f"{orden.consulta.turno.profesional.persona.get_full_name()} - N° Legajo: {orden.consulta.turno.profesional.numero_matricula}"
            }
            return JsonResponse(data)
        elif idMedicamento:
            medicamento = get_object_or_404(Medicaciones, pk=idMedicamento)
            data = {
                "idConsulta": medicamento.consulta.id,
                "id_medicamento": medicamento.id,
                "medicamento": medicamento.medicamento,
                "dosis": medicamento.dosis,
                "frecuencia": medicamento.frecuencia,
                "tiempoUso": medicamento.tiempo_uso,
                "profesional": f"{medicamento.consulta.turno.profesional.persona.get_full_name()} - N° Legajo: {medicamento.consulta.turno.profesional.numero_matricula}"
            }
            return JsonResponse(data)            
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)    

    if request.method == "POST":
        if form_consulta.is_valid() and estudios_formset.is_valid() and medicaciones_formset.is_valid():
            consulta = form_consulta.save(commit=False)
            consulta.turno = turno
            consulta.save()

            # Guardar estudios
            estudios = estudios_formset.save(commit=False)
            for estudio in estudios:
                estudio.consulta = consulta
                estudio.solicitado_por = request.user.usuario
                estudio.save()
            for obj in estudios_formset.deleted_objects: # Eliminar los marcados como DELETE
                obj.delete()

            # Guardar medicaciones
            medicaciones = medicaciones_formset.save(commit=False)
            for medicacion in medicaciones:
                medicacion.consulta = consulta
                medicacion.recetada_por = request.user.usuario
                medicacion.save()
            for obj in medicaciones_formset.deleted_objects:  # Eliminar los marcados como DELETE
                obj.delete()

            turno.asistio = True
            turno.estado = "atendido"
            turno.save()

            return redirect('turnosProgramados')

    context = {
        'form_consulta': form_consulta,
        'estudios_formset': estudios_formset,
        'medicaciones_formset': medicaciones_formset,
        'historialConsultas': consultas,
        'datos_turno': turno,
    }

    return render(request, 'medico/consultas/registroConsulta.html', context)

@medico_required
@login_required
def editarConsulta(request, id_consulta):
    hoy = timezone.localtime().date() 
    consulta = get_object_or_404(Consultas, id=id_consulta)
    turno = consulta.turno  
    especialidad = turno.especialidad

    if turno.fecha_turno != hoy or turno.profesional != request.user.usuario or turno.fecha_turno == hoy: 
        return HttpResponseForbidden(render(request, "403.html"))

    # historial de consultas del paciente en la misma especialidad
    consultas = Consultas.objects.filter(
        turno__paciente=turno.paciente,
        turno__especialidad=turno.especialidad
    ).prefetch_related('estudios', 'medicaciones').order_by('-fecha')[:10] 
    
                
    lista_estudios = EstudiosDiagnosticos.objects.filter(especialidad=especialidad)  # Estudios disponibles solo para esta especialidad
    
    form_consulta = FormConsulta(request.POST or None, instance=consulta)
    estudios_formset = EstudiosFormSet(request.POST or None, queryset=consulta.estudios.all(), prefix='estudios')
    medicaciones_formset = MedicacionesFormSet(request.POST or None, queryset=consulta.medicaciones.all(), prefix='medicaciones')

    # Limitar SIEMPRE el queryset de tipo_estudio
    for form in estudios_formset.forms:
        form.fields['tipo_estudio'].queryset = lista_estudios
        
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        idOrden = request.GET.get('idOrden')
        idMedicamento = request.GET.get('idMedicamento')
        if idOrden:
            orden = get_object_or_404(OrdenEstudio, pk=idOrden)
            data = {
                "idConsulta": orden.consulta.id,
                "id_orden": orden.id,
                "tipo_estudio": orden.tipo_estudio.nombre_estudio,
                "motivo": orden.motivo_estudio,
                "indicaciones": orden.indicaciones,
                "estado": orden.estado_detallado,
                "fecha_solicitud": orden.fecha_solicitud.date(),
                "profesional": f"{orden.consulta.turno.profesional.persona.get_full_name()} - N° Legajo: {orden.consulta.turno.profesional.numero_matricula}"
            }
            return JsonResponse(data)
        elif idMedicamento:
            medicamento = get_object_or_404(Medicaciones, pk=idMedicamento)
            data = {
                "idConsulta": medicamento.consulta.id,
                "id_medicamento": medicamento.id,
                "medicamento": medicamento.medicamento,
                "dosis": medicamento.dosis,
                "frecuencia": medicamento.frecuencia,
                "tiempoUso": medicamento.tiempo_uso,
                "profesional": f"{medicamento.consulta.turno.profesional.persona.get_full_name()} - N° Legajo: {medicamento.consulta.turno.profesional.numero_matricula}"
            }
            return JsonResponse(data)            
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)            
        

    if request.method == "POST":

        if not form_consulta.is_valid():
            print(form_consulta.errors.as_json())

        if not estudios_formset.is_valid():
            for form in estudios_formset.forms:
                print(form.errors.as_json())

        if not medicaciones_formset.is_valid():
            for form in medicaciones_formset.forms:
                print(form.errors.as_json())
        if form_consulta.is_valid() and estudios_formset.is_valid() and medicaciones_formset.is_valid():
            consulta = form_consulta.save(commit=False)
            consulta.turno = turno
            consulta.save()

            # Guardar estudios
            estudios = estudios_formset.save(commit=False)
            for estudio in estudios:
                estudio.consulta = consulta
                estudio.solicitado_por = request.user.usuario
                estudio.save()
            for obj in estudios_formset.deleted_objects: # Eliminar los marcados como DELETE
                obj.delete()

            # Guardar medicaciones
            medicaciones = medicaciones_formset.save(commit=False)
            for medicacion in medicaciones:
                medicacion.consulta = consulta
                medicacion.recetada_por = request.user.usuario
                medicacion.save()
            for obj in medicaciones_formset.deleted_objects:  # Eliminar los marcados como DELETE
                obj.delete()

            turno.asistio = True
            turno.estado = "atendido"
            turno.save()

            return redirect('turnosProgramados')

    context = {
        'form_consulta': form_consulta,
        'estudios_formset': estudios_formset,
        'medicaciones_formset': medicaciones_formset,
        'historialConsultas': consultas,
        'datos_turno': turno,
        'consulta': consulta,
        "edicion": True  
    }
    return render(request, 'medico/consultas/registroConsulta.html', context)

@medico_required
@login_required
def detallesConsulta(request, id_consulta):
    consulta = get_object_or_404(Consultas.objects.prefetch_related('estudios', 'medicaciones'),pk=id_consulta) 
    if consulta.turno.profesional != request.user.usuario: # Verificar si la consulta pertenece al profesional actual
        return HttpResponseForbidden(render(request, "403.html"))
    
    return render(request, 'medico/consultas/detallesConsulta.html', {"consulta":consulta})

@medico_required
@login_required
def historialConsultas(request):
    especialidad_id = request.session.get('especialidad_actual')
    if especialidad_id:
        especialidad = Especialidades.objects.get(id=especialidad_id)
    else:
        especialidad = False

    if especialidad:
        qs_base = Consultas.objects.filter(turno__profesional=request.user.usuario,turno__especialidad=especialidad).prefetch_related('estudios', 'medicaciones')
        filtro = ConsultasDelMedicoFilter(request.GET,queryset=qs_base)
        consultas = filtro.qs

        if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.GET.get("filtrar") == "1":
                return render(request,"medico/consultas/_tabla_consultasDelMedico.html",{"consultas": consultas,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
    else:
        consultas = Consultas.objects.none()
        filtro = ConsultasDelMedicoFilter(request.GET, queryset=consultas)
        
    return render(request,"medico/consultas/consultas.html",{"consultas": consultas, "filtro": filtro})


