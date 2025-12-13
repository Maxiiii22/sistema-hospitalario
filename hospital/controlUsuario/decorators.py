from functools import wraps
from django.shortcuts import redirect

def paciente_required(view_func):
    """
    Solo permitirá el acceso a la vista si el usuario es un paciente.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'paciente'):
            return view_func(request, *args, **kwargs)
        else:
            return redirect("unauthorized")  # Redirige a una página de acceso denegado
    return _wrapped_view


def personal_required(view_func):
    """
    Solo permitirá el acceso a la vista si el usuario es personal.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'usuario'):
            return view_func(request, *args, **kwargs)
        else:
            return redirect("unauthorized")  # Redirige a una página de acceso denegado
    return _wrapped_view

def superadmin_required(view_func):
    """Permite acceso solo a usuarios con tipoUsuario='Superadmin'."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user.usuario
        if hasattr(usuario, 'tipoUsuario') and usuario.tipoUsuario.id == 1: # Superadmin
            return view_func(request, *args, **kwargs)
        return redirect('unauthorized')
    return _wrapped_view

def administrador_required(view_func):
    """Permite acceso solo a usuarios con tipoUsuario='administrador'."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user.usuario
        if hasattr(usuario, 'tipoUsuario') and usuario.tipoUsuario.id == 2: # Administrador
            return view_func(request, *args, **kwargs)
        return redirect('unauthorized')
    return _wrapped_view

def medico_required(view_func):
    """Permite acceso solo a usuarios con tipoUsuario='Medico de consulta'."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user.usuario
        if hasattr(usuario, 'tipoUsuario') and usuario.tipoUsuario.id == 3: # Medico de consulta
            return view_func(request, *args, **kwargs)
        return redirect('unauthorized')
    return _wrapped_view

def enfermero_required(view_func):
    """Permite acceso solo a usuarios con tipoUsuario='Enfermero'."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user.usuario
        if hasattr(usuario, 'tipoUsuario') and usuario.tipoUsuario.id == 4: # Enfermero
            return view_func(request, *args, **kwargs)
        return redirect('unauthorized')
    return _wrapped_view


def operadorResultados_required(view_func):
    """Permite acceso solo a usuarios con tipoUsuario='OperadorResultados'."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user.usuario
        if hasattr(usuario, 'tipoUsuario') and usuario.tipoUsuario.id == 6: # OperadorResultados
            return view_func(request, *args, **kwargs)
        return redirect('unauthorized')
    return _wrapped_view

def jefeEnfermeria_required(view_func):
    """Permite acceso solo a usuarios con tipoUsuario='jefe de enfermeria'."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user.usuario
        if hasattr(usuario, 'tipoUsuario') and usuario.tipoUsuario.id == 7: # jefe enfermeria
            return view_func(request, *args, **kwargs)
        return redirect('unauthorized')
    return _wrapped_view

def medicoHospitalario_required(view_func):
    """Permite acceso solo a usuarios con tipoUsuario='Medico hospitalario'."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario = request.user.usuario
        if hasattr(usuario, 'tipoUsuario') and usuario.tipoUsuario.id == 8: # Medico hospitalario
            return view_func(request, *args, **kwargs)
        return redirect('unauthorized')
    return _wrapped_view