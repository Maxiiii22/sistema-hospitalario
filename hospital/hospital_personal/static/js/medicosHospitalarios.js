const modal = document.getElementById("editModal");
const formDelModal = document.getElementById("editForm");
const closeModalBtn = document.getElementById("closeEditModal");
const btnGuardar = document.querySelector(".btn-guardar");
const btnFormFilter= document.getElementById("btnformFilter");
const btnEvaluacionMedica = document.getElementById("btnEvaluacionMedica");
const btnAltaMedica = document.getElementById("btnAltaMedica");
const form = document.getElementById('filtro-form');

async function abrirModalDetalleObservacion(btn) {
    document.querySelector(".error-message-main")?.remove()
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-detalles-nota").style.display = "block" 
    let id_observacion = btn.dataset.idObservacionEnfermero;
    let id_asignacion_habitacion = btn.dataset.idAsignacionHabitacion;
    if(id_asignacion_habitacion){
        const btnFichaPaciente = document.getElementById("btnFichaPaciente");
        const baseUrl = btnFichaPaciente.dataset.urlbase;
        btnFichaPaciente.href = baseUrl.replace(/0\/?$/,id_asignacion_habitacion + "/");
    }
    document.getElementById("modal-title").textContent = `Detalles de la observación`;
    if(id_observacion){
        const url = new URL(window.location.href);
        url.searchParams.set("id_observacion", id_observacion);
        try {
            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });
    
            if (!response.ok) throw new Error("Error al obtener datos");
    
            const data = await response.json();
            document.getElementById("id_observaciones").value = data.observacion;
            document.getElementById("id_signos_vitales").value = data.signos_vitales;
            document.getElementById("id_procedimientos_realizados").value = data.procedimientos_realizados;
            document.getElementById("id_medicacion_administrada").value = data.medicacion_administrada;
            document.getElementById("id_observaciones").readOnly = true;
            document.getElementById("id_signos_vitales").readOnly = true;
            document.getElementById("id_procedimientos_realizados").readOnly = true;
            document.getElementById("id_medicacion_administrada").readOnly = true;
        } 
        catch (err) {
            alert("Error al cargar los datos");
            console.error(err);
        }
    }
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}




document.addEventListener("DOMContentLoaded", function () {
    if (document.querySelector(".errorModal")){
        modal.classList.add("show");
        document.body.style.overflow = "hidden"; 
        document.documentElement.style.overflow = "hidden";
    }


    const tablaGeneral = document.getElementById("box-tabla-general");
    if (tablaGeneral) {
        let timeout = null;
        form.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(async () => {
                const params = new URLSearchParams(new FormData(form));
                params.append('filtrar', '1');
                const response = await fetch(`?${params.toString()}`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const html = await response.text();
                tablaGeneral.innerHTML = html;
            }, 400);
        });    
    }



    const evaluaciones = document.querySelectorAll(".evaluacion-item");
    const btnVer = document.getElementById("btnVerAnterior");
    const btnOcultar = document.getElementById("btnOcultarUna");

    if(evaluaciones && btnVer){
        if (!btnVer || !btnOcultar) return;

        let visibleCount = 1;  

        btnVer.addEventListener("click", function () {
            if (visibleCount < evaluaciones.length) {
                evaluaciones[visibleCount].style.display = "block";
                visibleCount++;
            }

            if (visibleCount === evaluaciones.length) {
                btnVer.style.display = "none";
            }

            btnOcultar.style.display = "inline-block";
        });

        btnOcultar.addEventListener("click", function () {
            if (visibleCount > 1) {
                visibleCount--;
                evaluaciones[visibleCount].style.display = "none";
            }

            if (visibleCount === 1) {
                btnOcultar.style.display = "none";
            }

            btnVer.style.display = "inline-block";
        });
    }

    if (btnFormFilter){
        btnFormFilter.addEventListener("click",() => {  
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            const sff = document.getElementById("seccion-form-filter");             
            if(sff){
                sff.style.display = "block";
            }
            document.getElementById("modal-title").textContent = "Buscar por";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    }


    if (btnEvaluacionMedica){
        btnEvaluacionMedica.addEventListener("click",async () => { 
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-evaluacionMedica").style.display = "block";            
            document.getElementById("modal-title").textContent = "Nueva Evaluación Médica";
            let id_observacionMedico = btnEvaluacionMedica.dataset.idObservacionMedico;

            if(id_observacionMedico){
                const url = new URL(window.location.href);
                url.searchParams.set("id_observacionMedico", id_observacionMedico);
                try {
                    const response = await fetch(url, {
                        headers: {
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    });
            
                    if (!response.ok) throw new Error("Error al obtener datos");
            
                    const data = await response.json();
                    document.getElementById("id_motivo").value = data.motivo;
                    document.getElementById("id_motivo").readOnly = true;
                    document.getElementById("id_diagnostico").value = data.diagnostico;
                    document.getElementById("id_evolucion_clinica").value = data.evolucion_clinica;
                    document.getElementById("id_indicaciones").value = data.indicaciones;
                                
                } 
                catch (err) {
                    alert("Error al cargar los datos");
                    console.error(err);
                }
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    } 

    if (btnAltaMedica){
        btnAltaMedica.addEventListener("click",async () => { 
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-altaMedica").style.display = "block";            
            document.getElementById("modal-title").textContent = "Alta Médica";

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    } 
    

    if(closeModalBtn){
        closeModalBtn.addEventListener("click", () => {
            modal.classList.remove("show");
            modal.classList.remove("errorModal");
            document.body.style.overflow = "auto";
            document.documentElement.style.overflow = "auto";
        });
    }

    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("show");
            modal.classList.remove("errorModal");
            document.body.style.overflow = "auto";
            document.documentElement.style.overflow = "auto";

        }
    });

});

