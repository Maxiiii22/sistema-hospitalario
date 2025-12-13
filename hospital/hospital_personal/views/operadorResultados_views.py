
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required 
from controlUsuario.decorators import operadorResultados_required # En controlUsuario.decorators creamos decoradores personalizados que verifiquen si el usuario tiene el atributo de paciente o usuario, y redirigirlo a una página de acceso denegado si intenta acceder a una vista que no le corresponde.
from hospital_personal.models import UsuarioRolProfesionalAsignado,TurnoEstudio,ResultadoEstudio,ResultadoImagen
from hospital_personal.utils import generar_pdf_resultado
from hospital_personal.forms import ResultadoEstudioForm,ResultadoImagenForm
from django.forms import modelformset_factory
from django.contrib import messages


@operadorResultados_required
@login_required 
def verEstudios(request):
    rolesDelUsuario = UsuarioRolProfesionalAsignado.objects.filter(usuario=request.user.usuario)
    mapa_roles = {
        81: "lab",
        82: "img",
        83: "fisio",
        84: "eval"
    }

    tipoResultados = [
        mapa_roles[rol.rol_profesional.id]
        for rol in rolesDelUsuario
        if rol.rol_profesional.id in mapa_roles
    ]

    estudiosRealizados = TurnoEstudio.objects.filter(
        estado="analisis", 
        orden__tipo_estudio__tipo_resultado__in=tipoResultados
    )

    return render(request, "operadorResultados/estudiosRealizados.html", {"estudios": estudiosRealizados})

@operadorResultados_required
@login_required 
def cargar_resultado(request, turno_id):
    turno = get_object_or_404(TurnoEstudio, id=turno_id)

    if ResultadoEstudio.objects.filter(turno_estudio=turno).exists():  # Verificar si ya existe un resultado cargado
        messages.warning(request, "Ya se cargaron los resultados de este estudio.")
        return redirect("verEstudios")

    tipo = turno.orden.tipo_estudio.tipo_resultado
    resultado = ResultadoEstudio(turno_estudio=turno)

    if request.method == "POST":
        form = ResultadoEstudioForm(request.POST, request.FILES, turno=turno, instance=resultado)

        # Caso imágenes: permitir múltiples
        if tipo == "img":
            ImagenFormSet = modelformset_factory(ResultadoImagen, form=ResultadoImagenForm, extra=3, can_delete=True)
            formset = ImagenFormSet(request.POST, request.FILES, queryset=ResultadoImagen.objects.none())

            if form.is_valid() and formset.is_valid():
                resultado = form.save(commit=False)
                resultado.turno_estudio = turno
                resultado.cargado_por = request.user.usuario
                resultado.save()

                for f in formset.cleaned_data:
                    if f and f.get("imagen"):
                        imagen_obj = ResultadoImagen.objects.create(imagen=f["imagen"])
                        resultado.imagenes.add(imagen_obj) # Asociarla al ResultadoEstudio
                        
                generar_pdf_resultado(resultado)
                turno.estado = "realizado"
                turno.asistio = True
                turno.save()
                return redirect("verEstudios")

        else:
            # Laboratorio, fisiológicos o evaluaciones
            if form.is_valid():
                resultado = form.save(commit=False)

                resultado.turno_estudio = turno
                resultado.cargado_por = request.user.usuario
                resultado.save()

                generar_pdf_resultado(resultado)
                turno.estado = "realizado"
                turno.asistio = True
                turno.save()
                return redirect("verEstudios")
    else:
        form = ResultadoEstudioForm(turno=turno)

        if tipo == "img":
            ImagenFormSet = modelformset_factory(ResultadoImagen, form=ResultadoImagenForm, extra=3, can_delete=True)
            formset = ImagenFormSet(queryset=ResultadoImagen.objects.none())
            return render(request, "operadorResultados/cargar_resultado.html", {"form": form, "formset": formset, "turno": turno})

    return render(request, "operadorResultados/cargar_resultado.html", {"form": form, "turno": turno})