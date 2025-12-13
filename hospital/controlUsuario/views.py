from django.shortcuts import redirect, render
from .forms import FormularioLoginPersonalizado, FormularioRegistroPersonalizado
from django.contrib.auth import login # importamos la función login del módulo django.contrib.auth. Que se utiliza para autenticar a un usuario en una aplicación web, es decir, marca al usuario como autenticado y lo "logea" en el sistema. Esto significa que después de llamar a esta función, Django almacenará la información del usuario en la sesión, lo que le permitirá al usuario acceder a áreas de la aplicación que requieren estar autenticado.
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required  # Importamas el login_required que nos permite no poder acceder a rutas que necesitan que previamente estemos logueados. (No olvidarse de agregar la ruta login en settings.py)
from hospital_personal.models import Especialidades,ServicioDiagnostico
import datetime

# Create your views here.

def iniciar_sesion(request): 
    if request.method == "GET":
        return render(request, "login.html",{"form": FormularioLoginPersonalizado()})

    if request.method == "POST":
        form = FormularioLoginPersonalizado(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario) # Lo autentifica y lo mantiene logueado en la SESSION.   Esta función: Asocia al usuario autenticado con la sesión actual y Crea una cookie en el navegador del usuario para mantener la sesión activa.
            if hasattr(usuario, 'paciente'):
                return redirect("indexPaciente")
            elif hasattr(usuario, 'usuario'):
                return redirect("indexPersonal")
        else:
            return render(request, "login.html", {"form": form})


def signup(request):
    if request.method == "GET":
        return render(request,"signup.html", {"form": FormularioRegistroPersonalizado() })
    
    if request.method == "POST":
        form = FormularioRegistroPersonalizado(request.POST)  
        if form.is_valid():
            try:
                usuario = form.save(commit=True)
                login(request, usuario)
                return redirect('indexPaciente')
            except Exception as e:
                print(f"Error al guardar el usuario: {e}")
                # messages.error(request, "Ocurrió un error interno. Intenta nuevamente.")  
        else:
            # messages.error(request, "Formulario inválido. Revisa los datos ingresados.")      
            print("Formulario inválido. Revisa los datos ingresados.")
            
    return render(request, "signup.html", { "form" : form}) 


@login_required
def unauthorized(request):
    return render(request, "unauthorized.html")


@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect("login") 

def index(request):
    anio = datetime.date.today().year
    return render(request, "index.html",{"anio":anio})

def especialidades(request): 
    anio = datetime.date.today().year      
    allEspecialidades = Especialidades.objects.filter(permite_turno=True)
    return render(request, "especialidades.html",{"allEspecialidades":allEspecialidades,"anio":anio})

def serviciosDiagnostico(request):
    anio = datetime.date.today().year    
    allServicios = ServicioDiagnostico.objects.all()
    return render(request, "serviciosDiagnostico.html",{"allServicios":allServicios,"anio":anio})