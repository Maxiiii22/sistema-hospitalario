
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import personal_required # En controlUsuario.decorators creamos decoradores personalizados que verifiquen si el usuario tiene el atributo de paciente o usuario, y redirigirlo a una página de acceso denegado si intenta acceder a una vista que no le corresponde.
from controlUsuario.forms import FormularioActualizarPassword
from django.contrib.auth import update_session_auth_hash

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
        
    return render(request, "indexPersonal.html") 