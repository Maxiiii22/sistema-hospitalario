from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import enfermero_required
from hospital_personal.models import AsignacionesHabitaciones , AsignacionEnfermero,ObservacionesEnfermero,ObservacionesMedico,AltaMedica,Jorna_laboral
from hospital_personal.forms import FormularioEvaluacionMedica, FormularioNotaEnfermo
from hospital_personal.filters import PacientesAsignadosHabitacionEnfermeroFilter, ObservacionesDeEnfermerosFilter
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

@enfermero_required
@login_required
def listaPacientes(request):
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    id_jornada = asignacionTrabajo.get("idJornadaAsignada")
    if id_jornada is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los pacientes de su unidad.
        jornada = get_object_or_404(Jorna_laboral,pk=id_jornada)    
    
        qs_base = AsignacionEnfermero.objects.filter(enfermero=request.user.usuario,activo=True,jornada=jornada)    
    else:
        qs_base =  AsignacionEnfermero.objects.none() 
    
    filtro = PacientesAsignadosHabitacionEnfermeroFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    asignacionesEnfermero = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"enfermero/tablasDinamicas/_tabla_pacientes.html", {"asignacionesEnfermero": asignacionesEnfermero,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
    
    return render(request, "enfermero/listaPacientes.html", {"asignacionesEnfermero":asignacionesEnfermero,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@enfermero_required
@login_required
def notasEnfermeria(request,id_asignacionHabitacion):   
    if not AsignacionesHabitaciones.objects.filter(pk=id_asignacionHabitacion,enfermerosAsignados__enfermero=request.user.usuario,enfermerosAsignados__activo=True).exists(): 
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response 
    
    HabitacionAsignadaAEnfermero = AsignacionesHabitaciones.objects.get(pk=id_asignacionHabitacion,enfermerosAsignados__enfermero=request.user.usuario)
    
    qs_base = ObservacionesEnfermero.objects.filter(asignacion_enfermero__asignacion_habitacion=HabitacionAsignadaAEnfermero).order_by("-id")
    
    filtro = ObservacionesDeEnfermerosFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    observacionesEnfermeros = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"enfermero/tablasDinamicas/_tabla_notas_enfermeros.html", {"observacionesEnfermeros": observacionesEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()})    
        
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
    
    
    asignacionEnfermero = HabitacionAsignadaAEnfermero.enfermerosAsignados.first() 
    
    alta = AltaMedica.objects.filter(asignacion_medico__asignacion_habitacion=HabitacionAsignadaAEnfermero)
    if alta:
        return render(request, "enfermero/notasEnfermeria.html", {"observacionesEnfermeros":observacionesEnfermeros,"filtro":filtro,"alta":alta,"cantidad_registros_base":qs_base.count()}) 
    
    form = FormularioNotaEnfermo(initial={"asignacion_enfermero":asignacionEnfermero.id})
    
    if request.method == "POST":
        form = FormularioNotaEnfermo(request.POST,initial={"asignacion_enfermero":asignacionEnfermero.id})
        if form.is_valid():
            formNota = form.save()
            return redirect('notasEnfermeria-enfermero', id_asignacionHabitacion=formNota.asignacion_enfermero.asignacion_habitacion.id)
        else:
            return render(request, "enfermero/notasEnfermeria.html",{"observacionesEnfermeros":observacionesEnfermeros,"filtro":filtro,"form":form, "errorModal":True, "titleModal":"Nueva Nota","cantidad_registros_base":qs_base.count()})            
        
    return render(request, "enfermero/notasEnfermeria.html", {"observacionesEnfermeros":observacionesEnfermeros,"form":form,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@enfermero_required
@login_required
def fichaPaciente(request,id_asignacionHabitacion): 
    if not AsignacionesHabitaciones.objects.filter(pk=id_asignacionHabitacion,enfermerosAsignados__enfermero=request.user.usuario,enfermerosAsignados__activo=True).exists():
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response     
    
    HabitacionAsignadaAEnfermero = AsignacionesHabitaciones.objects.get(pk=id_asignacionHabitacion,enfermerosAsignados__enfermero=request.user.usuario)
    
    if ObservacionesMedico.objects.filter(asignacion_medico__asignacion_habitacion=HabitacionAsignadaAEnfermero).exists():
        observacionMedico = ObservacionesMedico.objects.filter(asignacion_medico__asignacion_habitacion=HabitacionAsignadaAEnfermero).order_by('-id').first()
        formReadOnly = FormularioEvaluacionMedica(instance=observacionMedico,readonly=True,prefix="form-readonly")
    else:
        formReadOnly = None
    
    alta = AltaMedica.objects.filter(asignacion_medico__asignacion_habitacion=HabitacionAsignadaAEnfermero).first()
    if not alta:
        alta = None
    
    
    return render(request, "enfermero/fichaPaciente.html",{"habitacionAsignada":HabitacionAsignadaAEnfermero,"formReadOnly":formReadOnly,"alta":alta}) 
