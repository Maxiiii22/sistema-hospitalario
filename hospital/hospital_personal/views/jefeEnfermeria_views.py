from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import jefeEnfermeria_required
from hospital_personal.models import Paciente,AsignacionesHabitaciones, AsignacionMedico, AsignacionEnfermero,Jorna_laboral,AltaMedica,AltaAdministrativa,UsuarioLugarTrabajoAsignado,ObservacionesEnfermero,ObservacionesMedico,Lugar
from hospital_personal.filters import PacienteFilter,EnfermerosDeLaUnidadFilter, ObservacionesDeEnfermeroFilter,EvaluacionesDelMedicoFilter, ObservacionesDeEnfermerosFilter
from hospital_personal.forms import FormularioAltaAdministrativa, FormularioCancelarAsignacionHabitacion, FormularioNotaEnfermo, FormularioEvaluacionMedica
from controlUsuario.models import Usuario
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from hospital_personal.forms import FormularioAsignarHabitacion, FormularioAsignarMedicoTratante, FormularioAsignarEnfermero
from dal import autocomplete
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Min


class MedicoTratanteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Solo usuarios autenticados pueden ver medicos tratantes
        if not self.request.user.is_authenticated:
            return Usuario.objects.none()

        qs = Usuario.objects.filter(tipoUsuario_id=8,persona__is_active=True) 

        if self.q:  # Filtra por lo que escribe el usuario
            qs = qs.filter(persona__first_name__icontains=self.q) | qs.filter(persona__last_name__icontains=self.q) | qs.filter(numero_matricula__icontains=self.q) | qs.filter(rolesProfesionalesUsuario__rol_profesional__nombre_rol_profesional__icontains=self.q)
        return qs
    
    def get_result_label(self, item):
        return f"{item.persona.get_full_name()} - N° Matricula: {item.numero_matricula} - Especializado en: {item.get_rolesProfesionales()}"

class EnfermeroAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Solo usuarios autenticados pueden ver enfermeros
        if not self.request.user.is_authenticated:
            return Usuario.objects.none()
        
        qs = Usuario.objects.none()
        
        id_jornadaLaboral = self.forwarded.get('jornada')  # Parámetro recibido desde "forward"
        if id_jornadaLaboral:
            qs = Usuario.objects.filter(tipoUsuario_id=4,UsuariosAsignadosAEsteLugar__jornada__id=id_jornadaLaboral,persona__is_active=True) 

        if self.q:  # Filtra por lo que escribe el usuario
            qs = qs.filter(persona__first_name__icontains=self.q) | qs.filter(persona__last_name__icontains=self.q) | qs.filter(numero_matricula__icontains=self.q) | qs.filter(rolesProfesionalesUsuario__rol_profesional__nombre_rol_profesional__icontains=self.q)
        return qs
    
    def get_result_label(self, item):
        return f"{item.persona.get_full_name()} - N° Matricula: {item.numero_matricula} - Especializado en: {item.get_rolesProfesionales()}"

#### Seccion Pacientes ####

@jefeEnfermeria_required
@login_required
def listaPacientes(request):       
    qs_base = Paciente.objects.filter(persona__is_active=True)
    filtro = PacienteFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    pacientes = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"jefeEnfermeria/pacientes/tablasDinamicas/_tabla_pacientes.html", {"allPacientes": pacientes,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
    return render(request, "jefeEnfermeria/pacientes/listaPacientes.html", {"allPacientes":pacientes,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@jefeEnfermeria_required
@login_required
def fichaPaciente(request,id_paciente):    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        idAsignacionHabitacion = request.GET.get('id_asignacion_habitacion')
        idAsignacionMedico = request.GET.get('id_asignacion_medico')
        
        if idAsignacionHabitacion:
            asignacion = get_object_or_404(AsignacionesHabitaciones, pk=idAsignacionHabitacion)
            data = {
                "id_asignacionHabitacion": asignacion.id,
                "id_lugarSeleccionado": asignacion.lugar.id          
            }
            return JsonResponse(data)
        elif idAsignacionMedico:
            asignacion = get_object_or_404(AsignacionMedico, pk=idAsignacionMedico)
            data = {
                "id_asignacionMedico": asignacion.id,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "ID no proporcionado"}, status=400)
        
    
    paciente = Paciente.objects.get(pk=id_paciente)
    hospitalizacionesAnteriores = AsignacionesHabitaciones.objects.filter(paciente=paciente,estado="finalizada")
    HabitacionAsignada = AsignacionesHabitaciones.objects.filter(paciente=paciente,estado="activa").first()
    formAsignarHab = FormularioAsignarHabitacion(initial={'paciente': paciente.id})
    
    MedicoTratanteAsignado = AsignacionMedico.objects.filter(asignacion_habitacion=HabitacionAsignada).first()
    EnfermerosAsignados = AsignacionEnfermero.objects.filter(asignacion_habitacion=HabitacionAsignada)
    
    formCancelarAsignacionHabitacion = None     
            
    if HabitacionAsignada:
        formAsignarMedicoTratante = FormularioAsignarMedicoTratante(initial={"asignacion_habitacion":HabitacionAsignada.id})   
        formAsignarEnfermero = FormularioAsignarEnfermero(initial={"asignacion_habitacion":HabitacionAsignada.id})
        if not MedicoTratanteAsignado:
            formCancelarAsignacionHabitacion = FormularioCancelarAsignacionHabitacion(initial={"asignacionHabitacion_id":HabitacionAsignada.id})         
    else:
        formAsignarMedicoTratante = None
        formAsignarEnfermero = None

    
    jornadas = Jorna_laboral.objects.exclude(turno="on-call")  
    enfermeros_por_dia = {}
    
    for jornada in jornadas:
        dia = jornada.get_dia_display().lower()
        turno = jornada.turno.lower()
        
        if dia not in enfermeros_por_dia:
            enfermeros_por_dia[dia] = {}
        
        enfermeros_por_dia[dia][turno] = {
            "horario": {
                "dia": "7:00 a 15:00",
                "tarde": "15:00 a 23:00",
                "noche": "23:00 a 7:00"
            }[turno],
            "enfermeros": [],
            "id_jornada": jornada.id
        }

    # Asignar los enfermeros
    for enfermero in EnfermerosAsignados:
        dia = enfermero.jornada.dia.lower()
        turno = enfermero.jornada.turno.lower()
        enfermeros_por_dia[dia][turno]["enfermeros"].append(enfermero)
    
    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

    conteo_por_dia = {}

    for dia in dias_semana:
        # Filtra enfermeros solo por día
        asignaciones = EnfermerosAsignados.filter(jornada__dia__iexact=dia)

        # De esos, contamos cuántos turnos distintos (dia/tarde/noche) ya están cubiertos
        turnos_cubiertos = asignaciones.values_list("jornada__turno", flat=True).distinct().count()

        conteo_por_dia[dia] = turnos_cubiertos
    
    hasAltaMedica = AltaMedica.objects.filter(asignacion_medico__asignacion_habitacion=HabitacionAsignada).first()
    if not hasAltaMedica:
        hasAltaMedica = None
        formAltaAdministrativa = None
    else:
        formAltaAdministrativa = FormularioAltaAdministrativa(initial={"paciente_id":paciente.id,"asignacionHabitacion_id":HabitacionAsignada.id})
    
    
    if request.method == 'POST':
        tipo_form = request.POST.get("tipo_form")
        
        if tipo_form == "formAsignarHab":      
            id_asignacionHabitacion = request.POST.get("id_instanceAsignacionHabitacion")  
        
            if id_asignacionHabitacion:
                if HabitacionAsignada.id != int(id_asignacionHabitacion):
                    response = render(request, "403.html", {
                        "mensaje": "No puedes modificar el registro de habitacion asignada"
                    })
                    response.status_code = 403
                    return response                 
                
                asignacionHabitacion = AsignacionesHabitaciones.objects.get(pk=id_asignacionHabitacion)
                formAsignarHab = FormularioAsignarHabitacion(request.POST,instance=asignacionHabitacion,initial={'paciente': paciente.id})     
            else:
                formAsignarHab = FormularioAsignarHabitacion(request.POST,initial={'paciente': paciente.id})     
            
            if formAsignarHab.is_valid():
                form = formAsignarHab.save()           
                return redirect('fichaPaciente', id_paciente=form.paciente.id)
            else:
                return render(request, "jefeEnfermeria/pacientes/fichaPaciente.html",{
                    "paciente":paciente,"habitacionAsignada":HabitacionAsignada , "formAsignarHab":formAsignarHab,"errorModal":True,
                    "errorFormAsignarHab":True, "titleModal":"Asignar habitación",
                    "formAsignarMedicoTratante":formAsignarMedicoTratante,"medicoTratante":MedicoTratanteAsignado,
                    "formAsignarEnfermero":formAsignarEnfermero, "enfermerosAsignados": EnfermerosAsignados,"enfermeros_por_dia": enfermeros_por_dia,"conteo_por_dia": conteo_por_dia,
                    "hasAltaMedica":hasAltaMedica,"formAltaAdministrativa":formAltaAdministrativa,"formCancelarAsignacionHabitacion":formCancelarAsignacionHabitacion,"hospitalizacionesAnteriores":hospitalizacionesAnteriores
                    })
            
        elif tipo_form == "formAsignarMedicoTratante":
            id_instanceMedicoTratante = request.POST.get("id_instanceMedicoTratante")  

            if id_instanceMedicoTratante:
                if MedicoTratanteAsignado.id != int(id_instanceMedicoTratante):
                    response = render(request, "403.html", {
                        "mensaje": "No puedes modificar el registro de la asignacion medica"
                    })
                    response.status_code = 403
                    return response    
                
                asignacionMedico = AsignacionMedico.objects.get(pk=id_instanceMedicoTratante)
                formAsignarMedicoTratante = FormularioAsignarMedicoTratante(request.POST,instance=asignacionMedico,initial={"asignacion_habitacion":HabitacionAsignada.id})                                                
            else:
                formAsignarMedicoTratante = FormularioAsignarMedicoTratante(request.POST,initial={"asignacion_habitacion":HabitacionAsignada.id})                
                
            if formAsignarMedicoTratante.is_valid():              
                form = formAsignarMedicoTratante.save()
                return redirect('fichaPaciente', id_paciente=form.asignacion_habitacion.paciente.id)
            else:
                return render(request, "jefeEnfermeria/pacientes/fichaPaciente.html",{
                    "paciente":paciente,"habitacionAsignada":HabitacionAsignada , "formAsignarHab":formAsignarHab,"errorModal":True,
                    "errorFormAsignarMedicoTratante":True, "titleModal":"Asignar médico hospitalario",
                    "formAsignarMedicoTratante":formAsignarMedicoTratante,"medicoTratante":MedicoTratanteAsignado,
                    "formAsignarEnfermero":formAsignarEnfermero, "enfermerosAsignados": EnfermerosAsignados,"enfermeros_por_dia": enfermeros_por_dia,"conteo_por_dia": conteo_por_dia,
                    "hasAltaMedica":hasAltaMedica,"formAltaAdministrativa":formAltaAdministrativa,"formCancelarAsignacionHabitacion":formCancelarAsignacionHabitacion,"hospitalizacionesAnteriores":hospitalizacionesAnteriores
                    })    
            
        elif tipo_form == "formAsignarEnfermero":
            id_instanceAsignacionEnfermero = request.POST.get("id_instanceAsignacionEnfermero")  

            if id_instanceAsignacionEnfermero:
                if not EnfermerosAsignados.filter(pk=int(id_instanceAsignacionEnfermero)).exists():
                    response = render(request, "403.html", {
                        "mensaje": "Ese registro no corresponde a esta asignacion"
                    })
                    response.status_code = 403
                    return response    
                
                asignacionEnfermero = AsignacionEnfermero.objects.get(pk=id_instanceAsignacionEnfermero)
                formAsignarEnfermero = FormularioAsignarEnfermero(request.POST,instance=asignacionEnfermero,initial={"asignacion_habitacion":HabitacionAsignada.id})                                                
            else:
                formAsignarEnfermero = FormularioAsignarEnfermero(request.POST,initial={"asignacion_habitacion":HabitacionAsignada.id})                
            
            if formAsignarEnfermero.is_valid():              
                form = formAsignarEnfermero.save()
                return redirect('fichaPaciente', id_paciente=form.asignacion_habitacion.paciente.id)
            else:
                return render(request, "jefeEnfermeria/pacientes/fichaPaciente.html",{
                    "paciente":paciente,"habitacionAsignada":HabitacionAsignada , "formAsignarHab":formAsignarHab,"errorModal":True,
                    "errorFormAsignarEnfermero":True, "titleModal":"Asignar enfermero",
                    "formAsignarMedicoTratante":formAsignarMedicoTratante,"medicoTratante":MedicoTratanteAsignado,
                    "formAsignarEnfermero":formAsignarEnfermero, "enfermerosAsignados": EnfermerosAsignados,"enfermeros_por_dia": enfermeros_por_dia,"conteo_por_dia": conteo_por_dia,
                    "hasAltaMedica":hasAltaMedica,"formAltaAdministrativa":formAltaAdministrativa,"formCancelarAsignacionHabitacion":formCancelarAsignacionHabitacion,"hospitalizacionesAnteriores":hospitalizacionesAnteriores
                    })
                
        elif tipo_form == "formAltaAdministrativa":
            formAltaAdministrativa = FormularioAltaAdministrativa(request.POST,initial={"paciente_id":paciente.id,"asignacionHabitacion_id":HabitacionAsignada.id})              
            
            if formAltaAdministrativa.is_valid():              
                try:
                    with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                        AltaAdministrativa.objects.create(
                            asignacion_habitacion=HabitacionAsignada,
                            responsable=request.user.usuario
                        )
                        HabitacionAsignada.estado = "finalizada"
                        HabitacionAsignada.fecha_salida = timezone.localtime() 
                        HabitacionAsignada.save()
                        HabitacionAsignada.enfermerosAsignados.update(activo=False)
                        HabitacionAsignada.medicoAsignado.update(activo=False)
                        
                    messages.success(request, "El alta administrativa se registró correctamente.")
                    return redirect('fichaPaciente', id_paciente=paciente.id)
                    
                except Exception as e:
                    messages.error(request, f"Ocurrió un error al registrar el alta administrativa: {str(e)}")
                
            else:
                for field, errors in formAltaAdministrativa.errors.items():
                    for error in errors:
                        if field == '__all__':  # errores de self.add_error(None, ...)
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{field}: {error}")   
                
                return render(request, "jefeEnfermeria/pacientes/fichaPaciente.html",{
                    "paciente":paciente,"habitacionAsignada":HabitacionAsignada , "formAsignarHab":formAsignarHab,
                    "formAsignarMedicoTratante":formAsignarMedicoTratante,"medicoTratante":MedicoTratanteAsignado,
                    "formAsignarEnfermero":formAsignarEnfermero, "enfermerosAsignados": EnfermerosAsignados,"enfermeros_por_dia": enfermeros_por_dia,"conteo_por_dia": conteo_por_dia,
                    "hasAltaMedica":hasAltaMedica,"formAltaAdministrativa":formAltaAdministrativa,"formCancelarAsignacionHabitacion":formCancelarAsignacionHabitacion,"hospitalizacionesAnteriores":hospitalizacionesAnteriores
                    })
                
        elif tipo_form == "formCancelarAsignacionHabitacion":
            formCancelarAsignacionHabitacion = FormularioCancelarAsignacionHabitacion(request.POST,initial={"asignacionHabitacion_id":HabitacionAsignada.id})              
            
            if formCancelarAsignacionHabitacion.is_valid():              
                HabitacionAsignada.delete()
                messages.success(request, "La asignacion se cancelo correctamente.")
                return redirect('fichaPaciente', id_paciente=paciente.id)                                
            else:
                for field, errors in formCancelarAsignacionHabitacion.errors.items():
                    for error in errors:
                        if field == '__all__':  # errores de self.add_error(None, ...)
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{field}: {error}")   
                
                return render(request, "jefeEnfermeria/pacientes/fichaPaciente.html",{
                    "paciente":paciente,"habitacionAsignada":HabitacionAsignada , "formAsignarHab":formAsignarHab,
                    "formAsignarMedicoTratante":formAsignarMedicoTratante,"medicoTratante":MedicoTratanteAsignado,
                    "formAsignarEnfermero":formAsignarEnfermero, "enfermerosAsignados": EnfermerosAsignados,"enfermeros_por_dia": enfermeros_por_dia,"conteo_por_dia": conteo_por_dia,
                    "hasAltaMedica":hasAltaMedica,"formAltaAdministrativa":formAltaAdministrativa,"formCancelarAsignacionHabitacion":formCancelarAsignacionHabitacion,"hospitalizacionesAnteriores":hospitalizacionesAnteriores
                    })
        
        
    return render(request, "jefeEnfermeria/pacientes/fichaPaciente.html",
                {"paciente":paciente,"formAsignarHab":formAsignarHab,"habitacionAsignada":HabitacionAsignada,
                "formAsignarMedicoTratante":formAsignarMedicoTratante,"medicoTratante":MedicoTratanteAsignado,
                "formAsignarEnfermero":formAsignarEnfermero, "enfermerosAsignados": EnfermerosAsignados,"enfermeros_por_dia": enfermeros_por_dia,"conteo_por_dia": conteo_por_dia,
                "hasAltaMedica":hasAltaMedica,"formAltaAdministrativa":formAltaAdministrativa,"formCancelarAsignacionHabitacion":formCancelarAsignacionHabitacion,"hospitalizacionesAnteriores":hospitalizacionesAnteriores
                }) 

@jefeEnfermeria_required
@login_required
def notasEnfermeria(request,id_hospitalizacion):   
    if not AsignacionesHabitaciones.objects.filter(pk=id_hospitalizacion).exists():
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response       
    
    hospitalizacion = AsignacionesHabitaciones.objects.get(pk=id_hospitalizacion)
    
    qs_base = ObservacionesEnfermero.objects.filter(asignacion_enfermero__asignacion_habitacion=hospitalizacion).order_by("-id")
    filtro = ObservacionesDeEnfermerosFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    observacionesEnfermeros = filtro.qs 
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"jefeEnfermeria/pacientes/tablasDinamicas/_tabla_notas_enfermeros.html", {"observacionesEnfermeros": observacionesEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()})    
        
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

        
    return render(request, "jefeEnfermeria/pacientes/notasEnfermeria.html", {"observacionesEnfermeros":observacionesEnfermeros,"filtro":filtro,"form":form,"cantidad_registros_base":qs_base.count()})   


@jefeEnfermeria_required
@login_required
def historialHospitalizacionPaciente(request,id_paciente):     
    paciente = get_object_or_404(Paciente, pk=id_paciente)  
        
    hospitalizaciones = AsignacionesHabitaciones.objects.filter(paciente=paciente,estado="finalizada").order_by("-id")
    if not hospitalizaciones.exists():
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response      

        
    return render(request, "jefeEnfermeria/pacientes/historialHospitalizacionPaciente.html", {"paciente":paciente,"hospitalizaciones":hospitalizaciones}) 

@jefeEnfermeria_required
@login_required
def fichaHospitalizacion(request,id_hospitalizacion):
    hospitalizacion = AsignacionesHabitaciones.objects.get(pk=id_hospitalizacion)
    medicoAsignado = AsignacionMedico.objects.get(asignacion_habitacion=hospitalizacion)     
    alta = AltaMedica.objects.filter(asignacion_medico__asignacion_habitacion=hospitalizacion).first()
    
    
    observaciones = ObservacionesMedico.objects.filter(asignacion_medico__asignacion_habitacion=hospitalizacion).order_by('-id')

    if observaciones.exists():
        formularios_evaluacion = []
        for eval in observaciones:
            formulario = FormularioEvaluacionMedica(instance=eval,readonly=True,prefix=f"form-readonly-{eval.id}")
            formularios_evaluacion.append(formulario)
        
        ultima_observacion = observaciones.first()
    else:
        formularios_evaluacion = None
        ultima_observacion = None
    
    
    return render(request, "jefeEnfermeria/pacientes/fichaHospitalizacion.html",{
                "hospitalizacion":hospitalizacion,"medicoAsignado":medicoAsignado,"alta":alta,"formularios_evaluacion":formularios_evaluacion,"ultima_observacion":ultima_observacion}) 


#### Fin Seccion Pacientes ####


#### Seccion Enfermeros ####

@jefeEnfermeria_required
@login_required
def enfermerosDeLaUnidad(request):
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)   
        enfermerosDeLaUnidad = (
            UsuarioLugarTrabajoAsignado.objects
                .filter(
                    lugar=lugar.unidad,
                    usuario__tipoUsuario_id=4,
                    usuario__persona__is_active=True
                )
                .values('usuario_id')         # Esto obliga a que los resultados sean diccionarios
                .annotate(id_min=Min('id'))   # Este es el ID del registro único por usuario
        )
        qs_base = UsuarioLugarTrabajoAsignado.objects.filter(
            id__in=[item['id_min'] for item in enfermerosDeLaUnidad]
        ) 
    else:
        qs_base = UsuarioLugarTrabajoAsignado.objects.none()
    
    filtro = EnfermerosDeLaUnidadFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    registroEnfermeros = filtro.qs
    
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"jefeEnfermeria/enfermeros/tablasDinamicas/_tabla_enfermeros.html", {"enfermerosDeLaUnidad": registroEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
    
        
    return render(request, "jefeEnfermeria/enfermeros/enfermerosDeLaUnidad.html", {"enfermerosDeLaUnidad":registroEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@jefeEnfermeria_required
@login_required
def fichaEnfermero(request,id_enfermero):
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)
        
        if not UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=id_enfermero,lugar=lugar.unidad,usuario__persona__is_active=True,usuario__tipoUsuario_id=4).exists():
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
    
    return render(request, "jefeEnfermeria/enfermeros/fichaEnfermero.html",{"enfermero":enfermero}) 


@jefeEnfermeria_required
@login_required
def historialNotasEnfermero(request,id_enfermero):   
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)    

        if not UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=id_enfermero,lugar=lugar.unidad,usuario__persona__is_active=True,usuario__tipoUsuario_id=4).exists():
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
                return render(request,"jefeEnfermeria/enfermeros/tablasDinamicas/_tabla_historial_notas_enfermero.html", {"observacionesEnfermeros": observacionesEnfermeros,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 
            
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

        
    return render(request, "jefeEnfermeria/enfermeros/historialNotasEnfermero.html", {"enfermero":enfermero,"observacionesEnfermeros":observacionesEnfermeros,"filtro":filtro,"form":form,"cantidad_registros_base":qs_base.count()}) 

#### Fin Seccion Enfermeros ####

#### Seccion Medicos ####

@jefeEnfermeria_required
@login_required
def medicosDeLaUnidad(request):
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los medicos de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)       
        medicosDeLaUnidad = (
            UsuarioLugarTrabajoAsignado.objects
                .filter(
                    lugar=lugar.unidad,
                    usuario__tipoUsuario_id=8,
                    usuario__persona__is_active=True
                )
                .values('usuario_id')         # Esto obliga a que los resultados sean diccionarios
                .annotate(id_min=Min('id'))   # Este es el ID del registro único por usuario
        )
        qs_base = UsuarioLugarTrabajoAsignado.objects.filter(
            id__in=[item['id_min'] for item in medicosDeLaUnidad]
        ) 
    else:
        qs_base = UsuarioLugarTrabajoAsignado.objects.none()
                
    filtro = EnfermerosDeLaUnidadFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
    registroMedicos = filtro.qs
        
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get("filtrar") == "1":
            return render(request,"jefeEnfermeria/medicos/tablasDinamicas/_tabla_medicos.html", {"medicosDeLaUnidad": registroMedicos,"filtro":filtro,"cantidad_registros_base":qs_base.count()})
        
        
        
    return render(request, "jefeEnfermeria/medicos/medicosDeLaUnidad.html", {"medicosDeLaUnidad":registroMedicos,"filtro":filtro,"cantidad_registros_base":qs_base.count()}) 

@jefeEnfermeria_required
@login_required
def fichaMedico(request,id_medico):
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)
        
        if not UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=id_medico,lugar=lugar.unidad,usuario__persona__is_active=True,usuario__tipoUsuario_id=8).exists():
            response = render(request, "403.html", {
                "mensaje": "No puedes acceder a esta asignacion"
            })
            response.status_code = 403
            return response 
    
        medico = get_object_or_404(Usuario, pk=id_medico)
    else:
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response         
    
    return render(request, "jefeEnfermeria/medicos/fichaMedico.html",{"medico":medico}) 


@jefeEnfermeria_required
@login_required
def historialEvaluacionesMedicas(request,id_medico):   
    asignacionTrabajo = request.user.usuario.get_asignacionActual()
    unidad = asignacionTrabajo.get("idLugarAsignacion")
    if unidad is not None:    # Si el jefe enfermeria accede en un dia/turno que no le corresponde no se le mostraran los enfermeros de su unidad.
        lugar = get_object_or_404(Lugar,pk=unidad)
        
        if not UsuarioLugarTrabajoAsignado.objects.filter(usuario_id=id_medico,lugar=lugar.unidad,usuario__persona__is_active=True,usuario__tipoUsuario_id=8).exists():
            response = render(request, "403.html", {
                "mensaje": "No puedes acceder a esta asignacion"
            })
            response.status_code = 403
            return response     
    
        medico = get_object_or_404(Usuario, pk=id_medico)
        qs_base = ObservacionesMedico.objects.filter(asignacion_medico__medico=medico).order_by("-id")
    
        filtro = EvaluacionesDelMedicoFilter(request.GET, queryset=qs_base, prefix="form-filter")  # El prefix en Django sirve para diferenciar varios formularios que usan los mismos nombres de campos dentro de la misma página. Es básicamente un “prefijo” que Django antepone a los name e id de los inputs del formulario.
        evaluacionesMedico = filtro.qs       
        
        if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':     
            if request.GET.get("filtrar") == "1":
                return render(request,"jefeEnfermeria/medicos/tablasDinamicas/_tabla_historial_evaluaciones_medicas.html", {"evaluacionesMedico": evaluacionesMedico,"filtro":filtro,"cantidad_registros_base":qs_base.count()})    
                            
            id_observacion = request.GET.get("id_observacion")
            if id_observacion:
                observacion = get_object_or_404(ObservacionesMedico, pk=id_observacion)
                data = {
                    "motivo": observacion.motivo,
                    "diagnostico": observacion.diagnostico,         
                    "evolucion_clinica": observacion.evolucion_clinica ,          
                    "indicaciones": observacion.indicaciones         
                }
                return JsonResponse(data)
            else:
                return JsonResponse({"error": "ID no proporcionado"}, status=400)
            
        form = FormularioEvaluacionMedica
    else:
        response = render(request, "403.html", {
            "mensaje": "No puedes acceder a esta asignacion"
        })
        response.status_code = 403
        return response             
    
    
    return render(request, "jefeEnfermeria/medicos/historialEvaluacionesMedicas.html", {"medico":medico,"evaluacionesMedico":evaluacionesMedico,"filtro":filtro,"form":form,"cantidad_registros_base":qs_base.count()}) 




#### Fin Seccion Medicos ####
