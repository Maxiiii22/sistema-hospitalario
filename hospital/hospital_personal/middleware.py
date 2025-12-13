from django.shortcuts import redirect
from django.contrib import messages

#    Middleware que redirige a los usuarios que deben cambiar su contraseña hacia la vista de cambio de contraseña, evitando que naveguen a otras URLs.
class ForzarCambioPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = [
            '/personal/cambiar-password/',
            '/admin/login/',
        ]

    def __call__(self, request):
        user = request.user
        path = request.path

        if user.is_authenticated:
            if hasattr(user, 'usuario') and user.usuario.debe_cambiar_contraseña:
                if path not in self.allowed_paths:
                    return redirect('/personal/cambiar-password/')

        return self.get_response(request)

# Middleware para mostrar el mensaje cuando se pasa del horario, Este middleware lo revisa en cada request.
class VerificarHorarioLaboralMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            if hasattr(request.user, 'usuario'):
                asignacion = request.user.usuario.get_asignacionActual()

                request.session.pop("sinAsignacion", None)                    
                request.session.pop("dia_no_laborable", None) 
                request.session.pop("fuera_de_turno", None) 
                
                sinAsignacion = not asignacion["asignacion"]
                
                if sinAsignacion:
                    request.session["sinAsignacion"] = sinAsignacion
                    return self.get_response(request)
                
                dia_no_laborable = not asignacion["dia_no_laborable"]
                
                if dia_no_laborable:
                    request.session["dia_no_laborable"] = dia_no_laborable
                    return self.get_response(request)                
                
                fuera_de_turno = not asignacion["dentro_del_turno"]                    
                request.session["fuera_de_turno"] = fuera_de_turno

                # Mostrar mensaje UNA SOLA VEZ cuando cambia a estado fuera-de-turno
                if fuera_de_turno:
                    if not request.session.get("mensaje_horario_mostrado", False):
                        request.session["mensaje_horario_mostrado"] = True
                else:
                    # Si vuelve a estar dentro del horario, reseteamos el flag
                    request.session["mensaje_horario_mostrado"] = False

            else:
                # si no está autenticado limpiamos flags
                request.session["mensaje_horario_mostrado"] = False
                request.session["fuera_de_turno"] = False

        return self.get_response(request)

