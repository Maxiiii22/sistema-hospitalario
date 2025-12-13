const modal = document.getElementById("editModal");
const formDelModal = document.getElementById("editForm");
const closeModalBtn = document.getElementById("closeEditModal");
const btnGuardar = document.querySelector(".btn-guardar");
const btnFormFilter= document.getElementById("btnformFilter");
const btnAsignarHabitacionPaciente = document.getElementById("btnAsignarHabitacionPaciente");
const btnCambiarHabitacionPaciente = document.getElementById("btnCambiarHabitacionPaciente");
const btnAsignarMedicoTratante = document.getElementById("btnAsignarMedicoTratante");
const btnCambiarMedicoTratante = document.getElementById("btnCambiarMedicoTratante");
const form = document.getElementById('filtro-form');


function resaltarElementoDesdeHash() {
    const hash = window.location.hash;
    if (hash) {
        const targetRow = document.querySelector(hash);
        if (targetRow) {
            targetRow.classList.add('resaltar');
            
            setTimeout(() => {
                targetRow.classList.remove('resaltar');
                history.replaceState(null, null, window.location.pathname + window.location.search);  // Quitar el hash de la URL sin recargar la página
            }, 3000);
        }
        else{
            setTimeout(() => {
                history.replaceState(null, null, window.location.pathname + window.location.search);  // Quitar el hash de la URL sin recargar la página
            }, 3000);      
        }
    }
}
window.addEventListener('hashchange', resaltarElementoDesdeHash); // // Ejecutar también cuando el hash cambie sin recargar la página


/* Esto es solo efecto de scroll */
const scrollable = document.querySelector('.box-radio');
if (scrollable){
const fade = document.querySelector('.fade-bottom');
scrollable.addEventListener('scroll', () => {
    const scrolledToBottom = scrollable.scrollTop + scrollable.clientHeight >= scrollable.scrollHeight - 1;

    fade.style.opacity = scrolledToBottom ? '0' : '1';
});
}

function toggleDia(dia) {
    const divActual = document.getElementById("item-dia-" + dia);
    const iconActual = document.getElementById("icon-arrow-" + dia);
    const estaOculto = divActual.classList.contains("hidden-linea");
    const todosLosDias = document.querySelectorAll(".asignacion-enfermero-turnos");
    const todosLosIconos = document.querySelectorAll("[id^='icon-arrow-']");

    todosLosDias.forEach(div => {
        div.classList.add("hidden-linea");
        div.classList.remove("visible-linea");
    });

    todosLosIconos.forEach(icon => {
        icon.classList.remove("darVuelta");
    });

    if (estaOculto) {
        divActual.classList.remove("hidden-linea");
        divActual.classList.add("visible-linea");
        iconActual.classList.add("darVuelta");
    }
}

function abrirModalAsignarEnfermero(btn) {
    document.querySelector(".error-message-main")?.remove()
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("id_instanceAsignacionEnfermero").disabled = true;
    document.getElementById("id_instanceAsignacionEnfermero").value = "";
    document.getElementById("seccion-asignarEnfermero").style.display = "block";
    let dia = btn.dataset.diaJornadaLaboral;
    let horario = btn.dataset.horarioJornadaLaboral;
    document.getElementById("id_jornada").value = btn.dataset.idJornadaLaboral;
    document.getElementById("modal-title").textContent = `Asignar enfermero el dia ${dia} de ${horario}`;
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}

function abrirModalCambiarEnfermero(btn) {
    document.querySelector(".error-message-main")?.remove()
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-asignarEnfermero").style.display = "block";
    let id_asignacion_enfermero = btn.dataset.idAsignacionEnfermero;
    document.getElementById("id_jornada").value = btn.dataset.idJornadaLaboral;
    document.getElementById("id_instanceAsignacionEnfermero").disabled = false;
    document.getElementById("id_instanceAsignacionEnfermero").value = id_asignacion_enfermero;
    document.getElementById("modal-title").textContent = `Cambiar enfermero`;
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}


async function abrirModalDetalleObservacion(btn) {
    document.querySelector(".error-message-main")?.remove()
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-detalles-nota").style.display = "block" 
    let id_observacion = btn.dataset.idObservacionEnfermero;
    let id_asignacion_habitacion = btn.dataset.idAsignacionHabitacion;
    let id_paciente = btn.dataset.idPaciente;
    const btnFichaPaciente = document.getElementById("btnFichaPaciente");
    if( btnFichaPaciente){
        if(id_asignacion_habitacion){
            const baseUrl = btnFichaPaciente.dataset.urlbaseFichaHospitalizacion;
            btnFichaPaciente.href = baseUrl.replace(/0\/?$/,id_asignacion_habitacion + "/");
        }
        else if(id_paciente){
            const baseUrl = btnFichaPaciente.dataset.urlbaseFichaPaciente;
            btnFichaPaciente.href = baseUrl.replace(/0\/?$/,id_paciente + "/");
        }
    }

    document.getElementById("modal-title").textContent = `Detalles de la observacion  `;
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

async function abrirModalDetalleEvaluacion(btn) {
    document.querySelector(".error-message-main")?.remove()
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-evaluacion-medica").style.display = "block";
    let id_observacion = btn.dataset.idObservacionMedico;
    let id_asignacion_habitacion = btn.dataset.idAsignacionHabitacion;
    let id_paciente = btn.dataset.idPaciente;
    const btnFichaPaciente = document.getElementById("btnFichaPaciente");
    if(id_asignacion_habitacion){
        const baseUrl = btnFichaPaciente.dataset.urlbaseFichaHospitalizacion;
        btnFichaPaciente.href = baseUrl.replace(/0\/?$/,id_asignacion_habitacion + "/");
    }
    else if(id_paciente){
        const baseUrl = btnFichaPaciente.dataset.urlbaseFichaPaciente;
        btnFichaPaciente.href = baseUrl.replace(/0\/?$/,id_paciente + "/");
    }

    document.getElementById("modal-title").textContent = `Detalles de la Evaluacion Médica`;
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
            document.getElementById("id_motivo").value = data.motivo;
            document.getElementById("id_diagnostico").value = data.diagnostico;
            document.getElementById("id_evolucion_clinica").value = data.evolucion_clinica;
            document.getElementById("id_indicaciones").value = data.indicaciones;
            document.getElementById("id_motivo").readOnly = true;
            document.getElementById("id_diagnostico").readOnly = true;
            document.getElementById("id_evolucion_clinica").readOnly = true;
            document.getElementById("id_indicaciones").readOnly = true;
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
            const seccionEdit = document.getElementById("seccion-edit");
            if(seccionEdit){
                seccionEdit.style.display ="none";
            }
            const sff = document.getElementById("seccion-form-filter");
            if(sff){
                sff.style.display="block";
            }
            document.getElementById("modal-title").textContent = "Buscar por";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    }

    if (btnAsignarHabitacionPaciente){
        btnAsignarHabitacionPaciente.addEventListener("click",() => { 
            document.getElementById("id_instanceAsignacionHabitacion").value = "";
            document.getElementById("id_instanceAsignacionHabitacion").disabled = true;
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-asignarHab").style.display = "block";
            document.getElementById("modal-title").textContent = "Asignar habitación";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    }    

    if (btnCambiarHabitacionPaciente){
        btnCambiarHabitacionPaciente.addEventListener("click",async ()  => { 
            document.getElementById("id_instanceAsignacionHabitacion").disabled = false;
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-asignarHab").style.display = "block";
            document.getElementById("modal-title").textContent = "Cambiar habitación";
            const id_asignacion_habitacion = btnCambiarHabitacionPaciente.dataset.idAsignacionHabitacion;

            const url = new URL(window.location.href);
            url.searchParams.set("id_asignacion_habitacion", id_asignacion_habitacion);
            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
        
                if (!response.ok) throw new Error("Error al obtener datos");
        
                const data = await response.json();
                document.getElementById("id_instanceAsignacionHabitacion").value = data.id_asignacionHabitacion;
                document.querySelectorAll(".box-radio").forEach(elemento => {
                    if(elemento.value == data.id_lugarSeleccionado){
                        elemento.checked = true;
                    }
                });
                            
            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    }    

    if (btnAsignarMedicoTratante){
        btnAsignarMedicoTratante.addEventListener("click",() => { 
            document.getElementById("id_instanceMedicoTratante").value = "";
            document.getElementById("id_instanceMedicoTratante").disabled == true;
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-asignarMedicoTratante").style.display = "block";
            document.getElementById("modal-title").textContent = "Asignar médico hospitalario";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    } 
    
    if (btnCambiarMedicoTratante){
        btnCambiarMedicoTratante.addEventListener("click",async ()  => { 
            document.getElementById("id_instanceMedicoTratante").disabled = false;
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-asignarMedicoTratante").style.display = "block";
            document.getElementById("modal-title").textContent = "Cambiar médico hospitalario";
            const id_asignacion_medico = btnCambiarMedicoTratante.dataset.idAsignacionMedico;

            const url = new URL(window.location.href);
            url.searchParams.set("id_asignacion_medico", id_asignacion_medico);
            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
        
                if (!response.ok) throw new Error("Error al obtener datos");
        
                const data = await response.json();
                document.getElementById("id_instanceMedicoTratante").value = data.id_asignacionMedico;
                            
            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }

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

