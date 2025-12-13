from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, JsonResponse, FileResponse
from hospital_personal.models import ResultadoEstudio
from django.contrib.auth.decorators import login_required 

# Create your views here.

@login_required
def ver_pdf_estudio(request, resultado_id):
    resultado = get_object_or_404(ResultadoEstudio, pk=resultado_id)
    persona_actual = request.user
    paciente = resultado.turno_estudio.orden.paciente.persona
    medico = resultado.turno_estudio.orden.solicitado_por.persona

    # Verificar permisos: paciente dueño o médico tratante
    if persona_actual != paciente and persona_actual != medico:
        response = render(request, "403.html", {
            "mensaje": "No tienes permiso para acceder a este archivo"
        })
        response.status_code = 403
        return response  
    
    return FileResponse(resultado.archivo_pdf.open(),  content_type='application/pdf')
