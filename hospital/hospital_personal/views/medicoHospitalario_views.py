from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import medicoHospitalario_required
from hospital_personal.models import AsignacionesHabitaciones, AsignacionMedico, ObservacionesEnfermero,ObservacionesMedico,UsuarioLugarTrabajoAsignado,AltaMedica,Lugar,AsignacionEnfermero
from hospital_personal.forms import FormularioEvaluacionMedica, FormularioNotaEnfermo, FormularioAltaMedica
from hospital_personal.filters import PacientesAsignadosHabitacionMedicoFilter, ObservacionesDeEnfermerosFilter, EnfermerosDeLaUnidadFilter, ObservacionesDeEnfermeroFilter
from controlUsuario.models import Usuario
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.db.models import Subquery, OuterRef, Min

@medicoHospitalario_required
@login_required
def listaPacientes(request):
    qs_base = AsignacionMedico.objects.filter(medico=request.user.usuario,asignacion_habitacion__estado="activa") 
    filtro = PacientesAsignadosHabitacionMedicoFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    asignacionesMedico = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"medicoHospitalario/pacientes/tablasDinamicas/_tabla_pacientes.html", {"asignacionesMedico": asignacionesMedico,"filtro":filtro,"cantidad_resgistros_base":qs_base.count()})
    
    
    return render(request, "medicoHospitalario/pacientes/listaPacientes.html", {"asignacionesMedico":asignacionesMedico,"filtro":filtro,"cantidad_resgistros_base":qs_base.count()}) 

@medicoHospitalario_required
@login_required
def notasEnfermeria(request,id_asignacionHabitacion):   
    if not AsignacionesHabitaciones.objects.filter(pk=id_asignacionHabitacion,medicoAsignado__medico=request.user.usuario).exists():
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response       
    
    HabitacionAsignadaAMedico = AsignacionesHabitaciones.objects.get(pk=id_asignacionHabitacion,medicoAsignado__medico=request.user.usuario)
    
    qs_base = ObservacionesEnfermero.objects.filter(asignacion_enfermero__asignacion_habitacion=HabitacionAsignadaAMedico).order_by("-id")
    
    filtro = ObservacionesDeEnfermerosFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    observacionesEnfermeros = filtro.qs 
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"medicoHospitalario/pacientes/tablasDinamicas/_tabla_notas_enfermeros.html", {"observacionesEnfermeros": observacionesEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()})    
        
        id_observacion = request.GET.get("id_observacion")
        if id_observacion:
            observacion = get_object_or_404(ObservacionesEnfermero, pk=id_observacion)
            data = {
                "observacion": observacion.observaciones,
                "signos_vitales": observacion.signos_vitales,         
                "procedimientos_realizados": observacion.procedimientos_realizados if observacion.procedimientos_realizados else "Sin procedimientos realizados" ,          
                "medicacion_administrada": observacion.medicacion_administrada if observacion.procedimientos_realizados else "Sin medicacion administrada"         
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)        
    
    form = FormularioNotaEnfermo()
        
    return render(request, "medicoHospitalario/pacientes/notasEnfermeria.html", {"observacionesEnfermeros":observacionesEnfermeros,"filtro":filtro,"form":form,"cantidad_registros_base":qs_base.count()}) 

@medicoHospitalario_required
@login_required
def fichaPaciente(request,id_asignacionHabitacion):
    if not AsignacionesHabitaciones.objects.filter(pk=id_asignacionHabitacion,medicoAsignado__medico=request.user.usuario).exists():
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response     
    
    HabitacionAsignadaAMedico = AsignacionesHabitaciones.objects.get(pk=id_asignacionHabitacion,medicoAsignado__medico=request.user.usuario)
    asignacionMedico = AsignacionMedico.objects.get(asignacion_habitacion=HabitacionAsignadaAMedico)     
    
    
    observaciones = ObservacionesMedico.objects.filter(asignacion_medico__asignacion_habitacion=HabitacionAsignadaAMedico).order_by('-id')

    if observaciones.exists():
        formularios_evaluacion = []
        for eval in observaciones:
            formulario = FormularioEvaluacionMedica(instance=eval,readonly=True,prefix=f"form-readonly-{eval.id}")
            formularios_evaluacion.append(formulario)
        
        ultima_observacion = observaciones.first()
    else:
        formularios_evaluacion = None
        ultima_observacion = None
    
    alta = AltaMedica.objects.filter(asignacion_medico__asignacion_habitacion=HabitacionAsignadaAMedico).first()
    if alta:
        return render(request, "medicoHospitalario/pacientes/fichaPaciente.html",{
                    "habitacionAsignada":HabitacionAsignadaAMedico,"formularios_evaluacion":formularios_evaluacion,"ultima_observacion":ultima_observacion,"alta":alta
                    }) 
    
    form = FormularioEvaluacionMedica(initial={'asignacion_medico': asignacionMedico.id})
    formAltaMedica = FormularioAltaMedica(initial={"asignacion_medico": asignacionMedico.id})
        
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_observacionMedico = request.GET.get('id_observacionMedico')
        
        if id_observacionMedico:
            observacionMedica = get_object_or_404(ObservacionesMedico, pk=id_observacionMedico)
            data = {
                "motivo": observacionMedica.motivo,
                "diagnostico": observacionMedica.diagnostico,          
                "evolucion_clinica": observacionMedica.evolucion_clinica,         
                "indicaciones": observacionMedica.indicaciones          
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)

        
    if request.method == "POST":
        tipo_form = request.POST.get("tipo_form")
        
        if tipo_form == "form_evaluacionMedica":
            form = FormularioEvaluacionMedica(request.POST,initial={'asignacion_medico': asignacionMedico.id})     
            
            if form.is_valid():
                formObs = form.save()           
                return redirect('fichaPaciente-medico-hospitalario', id_asignacionHabitacion=formObs.asignacion_medico.asignacion_habitacion.id)
            else:
                return render(request, "medicoHospitalario/pacientes/fichaPaciente.html",{
                    "habitacionAsignada":HabitacionAsignadaAMedico , "formularios_evaluacion":formularios_evaluacion,"ultima_observacion":ultima_observacion,
                    "form":form, "errorModal":True,"errorFormEvaluacionMedica":True, "titleModal":"Nueva Evaluación Médica",
                    "formAltaMedica":formAltaMedica
                    })
            
        elif tipo_form == "form_altaMedica":       
            formAltaMedica = FormularioAltaMedica(request.POST,initial={'asignacion_medico': asignacionMedico.id})     
            
            if formAltaMedica.is_valid():
                formAlta = formAltaMedica.save()           
                return redirect('fichaPaciente-medico-hospitalario', id_asignacionHabitacion=formAlta.asignacion_medico.asignacion_habitacion.id)
            else:
                return render(request, "medicoHospitalario/pacientes/fichaPaciente.html",{
                    "habitacionAsignada":HabitacionAsignadaAMedico , "formularios_evaluacion":formularios_evaluacion,"ultima_observacion":ultima_observacion,
                    "form":form,"formAltaMedica":formAltaMedica, "errorModal":True,"errorFormAltaMedica":True, "titleModal":"Alta Médica"
                    })
        else:
            response = render(request, "403.html", {
                "mensaje": "Formulario no reconocido."
            })
            response.status_code = 403
            return response             
    
    return render(request, "medicoHospitalario/pacientes/fichaPaciente.html",{
                "habitacionAsignada":HabitacionAsignadaAMedico,"formularios_evaluacion":formularios_evaluacion,"ultima_observacion":ultima_observacion,
                "form":form,"formAltaMedica":formAltaMedica
                }) 

@medicoHospitalario_required
@login_required
def enfermerosDeLaUnidad(request):
    misAsignacionesDeHospitalizacion = AsignacionMedico.objects.filter(medico=request.user.usuario,asignacion_habitacion__estado="activa").values_list('asignacion_habitacion_id', flat=True)
    misEnfermerosACargo = AsignacionEnfermero.objects.filter(asignacion_habitacion__id__in=misAsignacionesDeHospitalizacion,asignacion_habitacion__estado="activa").values("enfermero_id").annotate(id_min=Min("id"))
    enfermeros_ids = misEnfermerosACargo.values_list("enfermero_id",flat=True)
        
    subquery = UsuarioLugarTrabajoAsignado.objects.filter(
        usuario=OuterRef('usuario')
    ).values('usuario').annotate(
        id_min=Min('id')
    ).values('id_min')

    qs_base = UsuarioLugarTrabajoAsignado.objects.filter(
        id__in=Subquery(subquery),
        usuario__id__in=enfermeros_ids,
        usuario__tipoUsuario_id=4,
        usuario__persona__is_active=True
    )        

    
    filtro = EnfermerosDeLaUnidadFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    registroEnfermeros = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"medicoHospitalario/enfermeros/tablasDinamicas/_tabla_enfermeros.html", {"enfermerosDeLaUnidad": registroEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
    
        
    return render(request, "medicoHospitalario/enfermeros/enfermerosDeLaUnidad.html", {"enfermerosDeLaUnidad":registroEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@medicoHospitalario_required
@login_required
def fichaEnfermero(request,id_enfermero):
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el medico hospitalario accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)
        
        if not UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=id_enfermero,lugar=lugar,usuario__persona__is_active=True,usuario__tipoUsuario_id=4).exists():
            response = render(request, "403.html", {
                "mensaje": "No puedes acceder a esta asignacion"
            })
            response.status_code = 403
            return response 
    
        enfermero = get_object_or_404(Usuario, pk=id_enfermero)
    else:
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response 
    
    
    return render(request, "medicoHospitalario/enfermeros/fichaEnfermero.html",{"enfermero":enfermero}) 


@medicoHospitalario_required
@login_required
def historialNotasEnfermero(request,id_enfermero):   
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el medico hospitalario accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)
        
        if not UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=id_enfermero,lugar=lugar,usuario__persona__is_active=True,usuario__tipoUsuario_id=4).exists():
            response = render(request, "403.html", {
                "mensaje": "No puedes acceder a esta asignacion"
            })
            response.status_code = 403
            return response     
    
        enfermero = get_object_or_404(Usuario, pk=id_enfermero)
        
        qs_base = ObservacionesEnfermero.objects.filter(asignacion_enfermero__enfermero=enfermero).order_by("-id")
    
    
        filtro = ObservacionesDeEnfermeroFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
        observacionesEnfermeros = filtro.qs       
        
        if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':     
            if request.GET.get("filtrar") == "1":
                return render(request,"medicoHospitalario/enfermeros/tablasDinamicas/_tabla_historial_notas_enfermero.html", {"observacionesEnfermeros": observacionesEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()})    
                            
            id_observacion = request.GET.get("id_observacion")
            if id_observacion:
                observacion = get_object_or_404(ObservacionesEnfermero, pk=id_observacion)
                data = {
                    "observacion": observacion.observaciones,
                    "signos_vitales": observacion.signos_vitales,         
                    "procedimientos_realizados": observacion.procedimientos_realizados if observacion.procedimientos_realizados else "Sin procedimientos realizados" ,          
                    "medicacion_administrada": observacion.medicacion_administrada if observacion.procedimientos_realizados else "Sin medicacion administrada"         
                }
                return JsonResponse(data)
            else:
                return JsonResponse({"error": "ID no proporcionado"}, status=400)    
        

        form = FormularioNotaEnfermo()
    else:
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response          
        
    return render(request, "medicoHospitalario/enfermeros/historialNotasEnfermero.html", {"enfermero":enfermero,"observacionesEnfermeros":observacionesEnfermeros,"filtro":filtro,"form":form,"cantidad_registros_base":qs_base.count()}) 


