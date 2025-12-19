from django.shortcuts import redirect, render
from .forms import FormularioLoginPersonalizado, FormularioRegistroPersonalizado
from django.contrib.auth import login # importamos la función login del módulo django.contrib.auth. Que se utiliza para autenticar a un usuario en una aplicación web, es decir, marca al usuario como autenticado y lo "logea" en el sistema. Esto significa que después de llamar a esta función, Django almacenará la información del usuario en la sesión, lo que le permitirá al usuario acceder a áreas de la aplicación que requieren estar autenticado.
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required  # Importamas el login_required que nos permite no poder acceder a rutas que necesitan que previamente estemos logueados. (No olvidarse de agregar la ruta login en settings.py)
from hospital_personal.models import Especialidades,ServicioDiagnostico,SolicitudReactivacion
from hospital_pacientes.forms import SolicitudReactivacionForm
from controlUsuario.models import Persona
from controlUsuario.forms import FormularioNuevaPassword
import datetime
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db import transaction


# Create your views here.

def iniciar_sesion(request): 
    form = FormularioLoginPersonalizado()    

    if request.method == "POST":
        form = FormularioLoginPersonalizado(request, data=request.POST)
        if form.is_valid():
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    usuario = form.get_user()
                    login(request, usuario) # Lo autentifica y lo mantiene logueado en la SESSION.   Esta función: Asocia al usuario autenticado con la sesión actual y Crea una cookie en el navegador del usuario para mantener la sesión activa.
                    if hasattr(usuario, 'paciente'):
                        return redirect("indexPaciente")
                    elif hasattr(usuario, 'usuario'):
                        return redirect("indexPersonal")
            except Exception as e:
                messages.error(request, f"Ha ocurrido un inconveniente. Por favor, inténtelo nuevamente")
                return render(request, "public/login.html", {"form": form})
        else:
            return render(request, "public/login.html", {"form": form})
    
    return render(request, "public/login.html",{"form": form})
        


def signup(request):
    form = FormularioRegistroPersonalizado()
    
    if request.method == "POST":
        form = FormularioRegistroPersonalizado(request.POST)  
        if form.is_valid(): 
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    usuario = form.save(commit=True)
                    login(request, usuario)
                    return redirect('indexPaciente')
            except Exception as e:
                messages.error(request, "Ocurrió un error interno. Intenta nuevamente.")  
    
    return render(request, "public/signup.html", { "form" : form}) 


def index(request):
    anio = datetime.date.today().year
    return render(request, "public/index.html",{"anio":anio})

def especialidades(request): 
    anio = datetime.date.today().year      
    allEspecialidades = Especialidades.objects.filter(permite_turno=True)
    return render(request, "public/especialidades.html",{"allEspecialidades":allEspecialidades,"anio":anio})

def serviciosDiagnostico(request):
    anio = datetime.date.today().year    
    allServicios = ServicioDiagnostico.objects.all()
    return render(request, "public/serviciosDiagnostico.html",{"allServicios":allServicios,"anio":anio})



def reactivarServicios(request):
    form = SolicitudReactivacionForm()
    
    if request.method == "POST":
        form = SolicitudReactivacionForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data.get('dni')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')

            login_id = form.cleaned_data.get('login_id')
            telefono = form.cleaned_data.get('telefono')
            numero = form.cleaned_data.get('numero_paciente')
            observaciones = form.cleaned_data.get('observaciones')

            filtro = {
                'dni': dni,
                'first_name': first_name,
                'last_name': last_name,
                'fecha_nacimiento': fecha_nacimiento,
            }

            if login_id:
                filtro['persona__login_id'] = login_id
            if telefono:
                filtro['persona__telefono'] = telefono
            if numero:
                filtro['numero_paciente'] = numero

            try:
                persona = Persona.objects.get(is_active=False,**filtro)  
                paciente = persona.paciente
            except Persona.DoesNotExist:
                messages.error(request, "No se encontró ningún paciente con los datos proporcionados.")
                return render(request, "reactivacionCuenta/reactivarCuenta.html", {"form": form})

            if SolicitudReactivacion.objects.filter(paciente=paciente,estado="pendiente").exists():
                messages.error(request, "Ya hay una solicitud registrada para ese usuario.")
                return render(request, "reactivacionCuenta/reactivarCuenta.html", {"form": form})                
            
            solicitud = SolicitudReactivacion.objects.create(
                dni=dni,
                first_name=first_name,
                last_name=last_name,
                fecha_nacimiento=fecha_nacimiento,
                login_id=login_id if login_id else None,
                telefono=telefono if telefono else None,
                numero_paciente=numero if numero else None,
                observaciones=observaciones if observaciones else None,
                paciente=paciente
            )
            request.session["solicitud_reactivacion_id"] = solicitud.id
            return redirect('confirmacionDeSolicitud')
            
    return render(request, "reactivacionCuenta/reactivarCuenta.html", { "form" : form}) 

def confirmacionDeSolicitud(request):  
    try:
        solicitud_id = request.session.get("solicitud_reactivacion_id")    
        solicitud = SolicitudReactivacion.objects.get(pk=solicitud_id)
    except SolicitudReactivacion.DoesNotExist:
        response = render(request, "403.html", {
            "mensaje": "No tenés permiso para acceder a esta página o realizar esta acción."
            
        })
        response.status_code = 403
        return response     
    
    request.session.pop("solicitud_reactivacion_id", None)                    
    return render(request, "reactivacionCuenta/confirmacionDeSolicitud.html",{"solicitud":solicitud}) 

def seguimientoSolicitud(request):  
    if request.method == "POST":
        request.session.pop("id_solicitudReactivacion", None)                                                             
        codigo = request.POST.get("codigo_seguimiento")
        if not codigo:
            messages.error(request,"El campo no debe estar vacio.")
            return redirect("seguimientoSolicitud")
        
        solicitud = SolicitudReactivacion.objects.filter(codigo_seguimiento=codigo).first()
        if not solicitud:
            error = "No existe una solicitud de reactivación con ese código."
            return render(request, "reactivacionCuenta/seguimientoSolicitud.html",{"error":error,"codigo":codigo}) 
        else:
            if solicitud.estado == "aprobada":
                request.session["id_solicitudReactivacion"] = solicitud.id
                
            return render(request, "reactivacionCuenta/seguimientoSolicitud.html",{"solicitud":solicitud,"codigo":codigo}) 
            
        
    return render(request, "reactivacionCuenta/seguimientoSolicitud.html") 


def nuevaContra(request):
    try:
        solicitud_id = request.session.get("id_solicitudReactivacion")    
        solicitud = SolicitudReactivacion.objects.get(pk=solicitud_id)
    except SolicitudReactivacion.DoesNotExist:
        response = render(request, "403.html", {
            "mensaje": "No tenés permiso para acceder a esta página o realizar esta acción."
            
        })
        response.status_code = 403
        return response
    
    form = FormularioNuevaPassword(instance=solicitud.paciente.persona)

    if request.method == "POST":
        form = FormularioNuevaPassword(request.POST, instance=solicitud.paciente.persona)
        if form.is_valid():        
            try:
                with transaction.atomic(): # with transaction.atomic() → todo lo que está dentro se hace en una sola transacción. Si hay un error en cualquiera de las líneas, todo se revierte, no se guardan cambios parciales.
                    form.save()
                    solicitud.estado = "finalizado"
                    solicitud.save()
                    messages.success(request, "La operación se completó correctamente. Ahora puede iniciar sesión.")
                    request.session.pop("id_solicitudReactivacion", None)                                                     
                    return redirect("login")
            except Exception as e:
                messages.error(request, f"Ha ocurrido un inconveniente. Por favor, inténtelo nuevamente. Detalles: {str(e)}")
                return render(request, "reactivacionCuenta/nuevaContraseña.html", {"solicitud":solicitud,"form": form})
        else:
            return render(request, "reactivacionCuenta/nuevaContraseña.html", {"solicitud":solicitud,"form": form})
            
    

    return render(request, "reactivacionCuenta/nuevaContraseña.html", {"solicitud":solicitud,"form": form})



def unauthorized(request):
    return render(request, "unauthorized.html")


@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect("login") 
