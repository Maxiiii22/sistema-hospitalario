from django.urls import reverse

def enlace_info(request):
    # Inicializa las variables de enlace por defecto
    enlace_texto = ""
    enlace_url = ""

    # Solo si el usuario está autenticado y es paciente
    if request.user.is_authenticated and hasattr(request.user, 'paciente'):
        paciente = request.user.paciente  # Obtén el paciente relacionado con el usuario autenticado
        
        if paciente:  # Verifica que el paciente existe
            # Verifica si el paciente tiene menores a cargo
            if paciente.menores_a_cargo.exists():
                enlace_texto = "Gestionar menores a tu cargo"
                enlace_url = reverse("gestionMenores")  # Enlace para gestionar menores
            else:
                enlace_texto = "Registrar menor a cargo"
                enlace_url = reverse("registrarMenor")  # Enlace para registrar un menor

    # Devuelve las variables para que estén disponibles en el contexto global
    return {
        "enlace_texto": enlace_texto,
        "enlace_url": enlace_url,
    }
