from django.urls import path
from . import views 

urlpatterns = [
    path("", views.index, name="index"),
    path("especialidades", views.especialidades, name="especialidadesDelHospital"),
    path("servicios-diagnosticos", views.serviciosDiagnostico, name="serviciosDelHospital"),
    path("", views.index, name="index"),
    path("iniciar-sesion/", views.iniciar_sesion, name="login"),
    path("registrarse/", views.signup, name="signup"),
    path("unauthorized/", views.unauthorized, name="unauthorized"),
    path("logout/", views.cerrar_sesion, name="logout")
]