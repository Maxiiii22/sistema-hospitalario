const modal = document.getElementById("editModal");
const formDelModal = document.getElementById("editForm");
const closeModalBtn = document.getElementById("closeEditModal");
const btnGuardar = document.querySelector(".btn-guardar");
const btnNewTipoUsuario = document.getElementById("newTipoUsuario");
const btnNewRolProfesional = document.getElementById("newRolProfesional");
const btnNewDepartamento = document.getElementById("newDepartamento");
const btnNewEspecialidad = document.getElementById("newEspecialidad");
const btnNewLugarTrabajo = document.getElementById("newLugarTrabajo");
const btnNewAsignacion = document.getElementById("newAsignaciones");
const btnNewServicio= document.getElementById("newServicio");
const btnNewEstudio= document.getElementById("newEstudio");
const btnNewLugar= document.getElementById("newLugar");
const btnFormFilter= document.getElementById("btnformFilter");
const btnPlantillaEstudio= document.getElementById("newPlantillaEstudio");
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
const scrollable = document.querySelector('.box-multipleCheck');
if (scrollable){
const fade = document.querySelector('.fade-bottom');
scrollable.addEventListener('scroll', () => {
    const scrolledToBottom = scrollable.scrollTop + scrollable.clientHeight >= scrollable.scrollHeight - 1;

    fade.style.opacity = scrolledToBottom ? '0' : '1';
});
}


function abrirDetalle(btn) {
    document.getElementById("seccion-form-filter").style.display="none";
    document.getElementById("seccion-edit").style.display ="block";
    modal.classList.add("show");
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden"; 
    document.getElementById("modal-title").textContent = "Detalles del paciente"
    document.getElementById("modalTipoPaciente").innerHTML = btn.dataset.tipoPaciente;
    document.getElementById("modalPaciente").textContent = btn.dataset.paciente;
    document.getElementById("modalDni").textContent = btn.dataset.dni;
    document.getElementById("modalFechaNacimiento").textContent = btn.dataset.fechaNacimiento;
    document.getElementById("modalSexo").textContent = btn.dataset.sexo;
    document.getElementById("modalEmail").textContent = btn.dataset.email;
    document.getElementById("modalTelefono").textContent = btn.dataset.telefono;
    document.getElementById("modalDireccion").textContent = btn.dataset.direccion;
    document.getElementById("modalFechaRegistro").textContent = btn.dataset.fechaRegistro;
    document.getElementById("modalUltimoAcceso").textContent = btn.dataset.ultimoAcceso;
    document.getElementById("modalEstado").textContent = btn.dataset.estado;
}

function toggleTipoLugar(){
    const tipoLugar = document.getElementById("id_tipo");
        if(tipoLugar.value === "unidad_atenc"){
            document.getElementById("id_sala").value = "";
            document.getElementById("id_capacidad").value = "";
            document.getElementById("id_unidad").value = "";
            document.getElementById("id_sala").disabled = true;
            document.getElementById("id_capacidad").disabled = true;
            document.getElementById("id_unidad").disabled = true;
                
        }
        else{
            document.getElementById("id_sala").disabled = false;
            document.getElementById("id_capacidad").disabled = false;
            document.getElementById("id_unidad").disabled = false;
        }
}


async function obtenerDisponibilidadLugar(){
    const id_lugar = document.getElementById("id_lugar").value;
    const usuario_id = document.getElementById("identificadorUsuario").value;
    const container = document.querySelector("#seccion-lugarTrabajo");
    let urlGetDisponibilidadLugarTrabajo = document.getElementById("url-getLugarTrabajoDisponibilidad").value

    urlGetDisponibilidadLugarTrabajo = new URL(urlGetDisponibilidadLugarTrabajo, window.location.origin); // Django da una URL relativa → hay que agregarle el origin para que sea una ruta absoluta

    if (id_lugar === "") {
        const checkboxes = container.querySelectorAll('input[type="checkbox"][name="jornada"]');
        checkboxes.forEach(checkbox => {
            const label = checkbox.closest("label");
            if (label) {
            const originalText = label.getAttribute('data-original-text');
            if (originalText) {
                label.innerHTML = '';
                label.appendChild(checkbox);
                label.append(` ${originalText}`);
            }
            }
            checkbox.disabled = false;
            checkbox.checked = false;
            checkbox.style.cursor = "pointer";

        });
        return; // No seguimos al fetch si el valor es vacío
    }

    urlGetDisponibilidadLugarTrabajo.searchParams.append("id", id_lugar);
    urlGetDisponibilidadLugarTrabajo.searchParams.append("usuario_id", usuario_id);

    try {
        const response = await fetch(urlGetDisponibilidadLugarTrabajo, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) throw new Error("Error al obtener datos");

        const data = await response.json();       

        const disponibilidad = data.disponibilidad;

        const container = document.querySelector("#seccion-lugarTrabajo");

        for (const jornadaId in disponibilidad) {
            if (disponibilidad.hasOwnProperty(jornadaId)) {
                const jornadas = disponibilidad[jornadaId];
    
                jornadas.forEach(jornada => {
                    const checkbox = container.querySelector(`input[type="checkbox"][value="${jornada.id}"]`);
                    if (checkbox) {
                        const label = checkbox.closest("label");
                        if (label) {
                            const originalText = label.getAttribute('data-original-text') || label.innerText.trim();
                            label.setAttribute('data-original-text', originalText);
                
                            // Limpiar el contenido y restaurar
                            checkbox.disabled = false;
                            checkbox.style.cursor = "pointer";
                            label.innerHTML = '';
                            label.appendChild(checkbox);
                            label.append(` ${originalText} - ${jornada.estado} (${jornada.cantidad}/${jornada.maxCantidad})${jornada.Disponible != null ? ' - ' + jornada.Disponible : ''}`);

                            if (jornada.Disponible != null || jornada.cantidad == jornada.maxCantidad ){
                                checkbox.disabled = true;
                                checkbox.style.cursor = "not-allowed"
                                checkbox.checked = false
                            }
                        }
                    }
                });
            }
        }
    } 
    catch (err) {
        alert("Error al cargar los datos");
        console.error(err);
    }
}


document.addEventListener("DOMContentLoaded", function () {
    if (document.querySelector(".errorModal")){
        modal.classList.add("show");
        document.body.style.overflow = "hidden"; 
        document.documentElement.style.overflow = "hidden";
    }
    
    const tablaGeneral = document.getElementById("box-tabla-general"); 
    if (tablaGeneral) {  /* Filtro */
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

    const tablaEspecialidades = document.getElementById("tabla-gestion-especialidades");
    if (tablaEspecialidades) {
        tablaGeneral.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_especialidad = btn.dataset.idEspecialidad;
            if (!id_especialidad) return;

            document.getElementById("modal-title").textContent = "Editar especialidad";

            const url = new URL(window.location.href);
            url.searchParams.set("id", id_especialidad);
            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
        
                if (!response.ok) throw new Error("Error al obtener datos");
        
                const data = await response.json();
                document.querySelectorAll(".error-message").forEach(div => div.remove());
                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block";

                document.getElementById("id_especialidad").value = data.id;
                document.getElementById("id_nombre_especialidad").value = data.nombre_especialidad;
                if(data.permite_turno){
                    document.getElementById("id_permite_turno").checked = true;
                }
                else{
                    document.getElementById("id_permite_turno").checked = false;
                }
                document.getElementById("id_capacidad_diaria").value = data.capacidad_diaria;
                document.getElementById("id_descripcion").value = data.descripcion;
                document.getElementById("id_departamento").value = data.departamento;
            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";            
        });
    
    }
    
    const tablaServicios = document.getElementById("tabla-gestion-servicios-diagnostico");
    if (tablaServicios) {
        tablaGeneral.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_servicio = btn.dataset.idServicio;
            if (!id_servicio) return;

            document.getElementById("modal-title").textContent = "Editar servicio de diagnostico";

            const url = new URL(window.location.href);
            url.searchParams.set("id", id_servicio);
            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
        
                if (!response.ok) throw new Error("Error al obtener datos");
        
                const data = await response.json();
                document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block";
                
                document.getElementById("id_servicio").value = data.id_servicio;
                document.getElementById("id_nombre_servicio").value = data.nombre_servicio;
                document.getElementById("id_descripcion").value = data.descripcion_servicio;
                document.getElementById("id_capacidad_diaria").value = data.capacidad_diaria_servicio;
                document.getElementById("id_departamento").value = data.departamento_servicio;

                const lugaresIds = data.lugar_servicio;
                const checkboxes = document.querySelectorAll('input[name="lugar"]');
                checkboxes.forEach((checkbox) => {
                    checkbox.checked = lugaresIds.includes(parseInt(checkbox.value));
                });   

                
            } 
            catch (err) {
                alert("Error al cargar los datos del lugar");
                console.error(err);
            }
            
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        });  
    }

    const tablaEstudios = document.getElementById("tabla-gestion-estudios-diagnostico");
    if (tablaEstudios) {
        tablaGeneral.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_estudio = btn.dataset.idEstudio;
            if (!id_estudio) return;


            document.getElementById("modal-title").textContent = "Editar estudio de diagnostico";
            const url = new URL(window.location.href);
            url.searchParams.set("id", id_estudio);

            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
            
                if (!response.ok) throw new Error("Error al obtener datos");
            
                const data = await response.json();

                document.querySelectorAll(".error-message").forEach(div => div.remove());
                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block";
    
                document.querySelector(".modal-content").style.width = "fit-content";
                document.getElementById("id_estudio").value = data.id_estudio;
                document.getElementById("id_nombre_estudio").value = data.nombre_estudio;
                document.getElementById("id_servicio_diagnostico").value = data.servicio_estudio;
                document.getElementById("id_tipo_resultado").value = data.tipo_resultado; 
    
                const especialidadesIds = data.especialidad_estudio;
                const checkboxes = document.querySelectorAll('input[name="especialidad"]');
                checkboxes.forEach((checkbox) => {
                    checkbox.checked = especialidadesIds.includes(parseInt(checkbox.value));
                });  
            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        });  

    }


    const tablaPlantillaEstudios = document.getElementById("tabla-gestion-plantilla-estudio");
    if (tablaPlantillaEstudios) {
        tablaGeneral.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_plantilla_estudio = btn.dataset.idPlantillaEstudio;
            if (!id_plantilla_estudio) return;

            document.getElementById("modal-title").textContent = "Editar plantilla estudio";

            const url = new URL(window.location.href);
            url.searchParams.set("id", id_plantilla_estudio);

            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
    
                if (!response.ok) throw new Error("Error al obtener datos");
    
                const data = await response.json();
                
                document.querySelectorAll(".error-message").forEach(div => div.remove());
                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block"; 
                
                document.getElementById("id_plantilla").value = data.id_plantilla;
                document.getElementById("id_estudio").value = data.estudio_plantilla;
                document.getElementById("id_estructura").value = JSON.stringify(data.estructura_estudio, null, 2);


            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";            
        }); 

    }    

    const tablaLugares = document.getElementById("tabla-gestion-lugares");
    if (tablaLugares) {
        tablaGeneral.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_lugar = btn.dataset.idLugar;
            if (!id_lugar) return;

            document.getElementById("modal-title").textContent = "Editar lugar";

            const url = new URL(window.location.href);
            url.searchParams.set("id", id_lugar);

            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
                if (!response.ok) throw new Error("Error al obtener datos");

                const data = await response.json();

                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block";
                document.querySelectorAll(".error-message").forEach(div => div.remove());
                document.getElementById("id_lugar").value = data.id_lugar;
                document.getElementById("id_nombre").value = data.nombre_lugar;
                document.getElementById("id_tipo").value = data.tipo_lugar;
                document.getElementById("id_piso").value = data.piso_lugar;
                document.getElementById("id_sala").value = data.sala_lugar;
                document.getElementById("id_abreviacion").value = data.abreviacion_lugar;
                document.getElementById("id_capacidad").value = data.capacidad_lugar;
                if (data.departamento_lugar){
                    document.getElementById("id_departamento").value = data.departamento_lugar;
                }
                if (data.unidad_lugar){
                    document.getElementById("id_unidad").value = data.unidad_lugar;
                }
                document.getElementById("id_descripcion").value = data.descripcion_lugar || "";
                document.getElementById("id_es_critico").checked = data.isCritico_lugar;
                document.getElementById("id_activo").checked = data.isActivo_lugar;
                toggleTipoLugar();


            } catch (err) {
                alert("Error al cargar los datos del lugar");
                console.error(err);
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden";
            document.documentElement.style.overflow = "hidden";            
        });

        document.getElementById("id_tipo").addEventListener('change', toggleTipoLugar);  

    }

    const tablaDepartamentos = document.getElementById("tabla-departamentos");
    if (tablaDepartamentos) {
        tablaGeneral.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_departamento = btn.dataset.idDepartamento;
            if (!id_departamento) return;

            const url = new URL(window.location.href);
            url.searchParams.set("id", id_departamento);
            document.getElementById("modal-title").textContent = "Editar departamento";
            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
    
                if (!response.ok) throw new Error("Error al obtener datos");
    
                const data = await response.json();
    
                document.querySelectorAll(".error-message").forEach(div => div.remove());
                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block"; 
                document.getElementById("id_departamento").value = data.id_departamento;
                document.getElementById("id_nombre_departamento").value = data.nombre_departamento;
                document.getElementById("id_tipo").value = data.tipo;
                document.getElementById("id_descripcion").value = data.descripcion;
    

                
            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";            
        });

    }

    const tablaTipoUsuarios = document.getElementById("tabla-tipo-usuarios");
    if (tablaTipoUsuarios) {
        tablaTipoUsuarios.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_tipo_usuario = btn.dataset.idTipoUsuario;
            if (!id_tipo_usuario) return;


            document.getElementById("modal-title").textContent = "Editar tipo de usuario";
            const url = new URL(window.location.href);
            url.searchParams.set("id_tipo_usuario", id_tipo_usuario);

            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
    
                if (!response.ok) throw new Error("Error al obtener datos");
    
                const data = await response.json();

                document.querySelector(".error-message-main")?.remove();
                document.querySelectorAll(".error-message").forEach(div => div.remove());
                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block";                 
                document.querySelector(".seccion-rol-profesional").style.display = "none";
                document.querySelector(".seccion-tipo-usuario").style.display = "block";
                document.getElementById("id_tipo_usuario").value = data.id_tipo_usuario;
                document.getElementById("id_nombre_tipoUsuario").value = data.nombre_tipo_usuario;

            }
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";            
        });
    }


    const tablaRolesProfesionales = document.getElementById("tabla-gestion-rolesProfesionales");
    if (tablaRolesProfesionales) {
        tablaGeneral.addEventListener("click", async (e) => {
            const btn = e.target.closest(".btn-masDetalles");
            if (!btn) return;

            const id_rol_profesional = btn.dataset.idRolProfesional;
            if (!id_rol_profesional) return;


            document.getElementById("modal-title").textContent = "Editar rol profesional";
            const url = new URL(window.location.href);
            url.searchParams.set("id_rol_profesional", id_rol_profesional);

            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
    
                if (!response.ok) throw new Error("Error al obtener datos");
    
                const data = await response.json();
                
                document.querySelector(".error-message-main")?.remove();
                document.querySelectorAll(".error-message").forEach(div => div.remove());
                document.getElementById("seccion-form-filter").style.display="none"
                document.getElementById("seccion-edit").style.display ="block";                 
                document.querySelector(".seccion-rol-profesional").style.display = "block";
                document.querySelector(".seccion-tipo-usuario").style.display = "none";
                document.getElementById("id_rol_profesional").value = data.id_rol_profesional;
                document.getElementById("id_nombre_rol_profesional").value = data.nombre_rol_profesional;
                document.getElementById("id_tipoUsuario").value = data.tipo_usuario;
                document.getElementById("id_especialidad").value = data.id_especialidad;
                document.getElementById("id_servicio_diagnostico").value = data.id_servicio;
                document.getElementById("id_departamento").value = data.id_departamento;
                toggleFields();
    
                
            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";            
        });   
    }


    if (btnFormFilter){
        btnFormFilter.addEventListener("click",() => {  
            const seccionEdit = document.getElementById("seccion-edit");
            if(seccionEdit){
                seccionEdit.style.display ="none";
            }
            document.getElementById("seccion-form-filter").style.display="block";
            document.getElementById("modal-title").textContent = "Buscar por";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    }

    if (btnNewTipoUsuario){
        btnNewTipoUsuario.addEventListener("click",() => {
            document.querySelector(".error-message-main")?.remove();
            document.querySelectorAll(".error-message").forEach(div => div.remove());
            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";                 
            document.querySelector(".seccion-rol-profesional").style.display = "none";
            document.querySelector(".seccion-tipo-usuario").style.display = "block";
            document.getElementById("id_tipo_usuario").value = "";
            document.getElementById("id_nombre_tipoUsuario").value = "";
            document.getElementById("modal-title").textContent = "Nuevo tipo de usuario";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        document.querySelector("#editForm.formTipoUsuario").addEventListener("submit", function(event) {
            event.preventDefault();
    
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

    
            // Seleccionar todos los inputs, select y textarea
            const allinputsModal = document.querySelectorAll("#editForm.formTipoUsuario .campo-input input, #editForm.formTipoUsuario select, #editForm.formTipoUsuario textarea");
    
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim()) {
                    hayErrores = true;
                    let mensajeError = '';
    
                    // Verifica el campo y muestra un mensaje de error específico
                    if (input.id === 'id_nombre_tipoUsuario') {
                        mensajeError = 'El nombre del tipo de usuario es obligatorio.';
                    }
    
                    errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                    input.parentElement.appendChild(errorDiv); 
                }
            });
    
            if (!hayErrores) {
                document.querySelector("#editForm.formTipoUsuario").submit();
            }
        });
    }

    if (btnNewRolProfesional){
        btnNewRolProfesional.addEventListener("click",() => {
            document.querySelector(".error-message-main")?.remove();
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";  
            document.querySelector(".seccion-rol-profesional").style.display = "block";
            document.querySelector(".seccion-tipo-usuario").style.display = "none";
            document.getElementById("id_rol_profesional").value = "";
            document.getElementById("id_nombre_rol_profesional").value = "";
            document.getElementById("id_tipoUsuario").value = "";
            document.getElementById("id_especialidad").value = "";
            document.getElementById("id_servicio_diagnostico").value = "";
            document.getElementById("seccion-especialidad").style.display="block";
            document.getElementById("seccion-servicio_diagnostico").style.display="block";
            document.getElementById("seccion-departamento").style.display="block";
            toggleFields();

            document.getElementById("modal-title").textContent = "Nuevo rol profesional";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    
        document.querySelector("#editForm.formRolProfesional").addEventListener("submit", function(event) {
            event.preventDefault();
    
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

    
            // Seleccionar todos los inputs, select y textarea
            const allinputsModal = document.querySelectorAll("#editForm.formRolProfesional .campo-input input, #editForm.formRolProfesional select, #editForm.formRolProfesional textarea");
    
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim() && !input.disabled) {
                    hayErrores = true;
                    console.log(input)
                    let mensajeError = '';
    
                    if (input.id === 'id_nombre_rol_profesional') {
                        mensajeError = 'El nombre del rol profesional es obligatorio.';
                    } 
                    else if (input.id === 'id_tipoUsuario') {
                        mensajeError = 'Por favor, seleccione un tipo de usuario.';
                    }
                    else if (input.id === 'id_especialidad') {
                        mensajeError = 'Por favor, seleccione una opcion.';
                    }
                    else if (input.id === 'id_servicio_diagnostico') {
                        mensajeError = 'Por favor, seleccione una opcion.';
                    }
                    else if (input.id === 'id_departamento') {
                        mensajeError = 'Por favor, seleccione una opcion.';
                    }
    
                    errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                    input.parentElement.appendChild(errorDiv); 
                }
            });
    
            if (!hayErrores) {
                document.querySelector("#editForm.formRolProfesional").submit();
            }
        });
    }

    if (btnNewDepartamento){
        btnNewDepartamento.addEventListener("click",() => {
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";            
            document.getElementById("id_departamento").value = "";
            document.getElementById("id_nombre_departamento").value = "";
            document.getElementById("id_tipo").value = "";
            document.getElementById("id_descripcion").value = "";
            document.getElementById("modal-title").textContent = "Nuevo departamento";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        formDelModal.addEventListener("submit", function(event) {
            event.preventDefault();
    
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

    
            // Seleccionar todos los inputs, select y textarea
            const seccionEdit = document.getElementById("seccion-edit");
            const allinputsModal = seccionEdit.querySelectorAll(".campo-input input,.campo-input select,.campo-input textarea");
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim()) {
                    hayErrores = true;
                    let mensajeError = '';
    
                    // Verifica el campo y muestra un mensaje de error específico
                    if (input.id === 'id_nombre_departamento') {
                        mensajeError = 'El nombre de la departamento es obligatorio.';
                    } else if (input.id === 'id_tipo') {
                        mensajeError = 'El tipo es obligatorio.';
                    } else if (input.id === 'id_descripcion') {
                        mensajeError = 'La descripción es obligatoria.';
                    }
    
                    errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                    input.parentElement.appendChild(errorDiv); 
                }
            });
    
            if (!hayErrores) {
                formDelModal.submit();
            }
        });
    }

    if (btnNewEspecialidad){
        btnNewEspecialidad.addEventListener("click",() => {
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";
            document.getElementById("id_especialidad").value = "";
            document.getElementById("id_nombre_especialidad").value = "";
            document.getElementById("id_permite_turno").checked = false;
            document.getElementById("id_capacidad_diaria").value = "";
            document.getElementById("id_departamento").value = "";
            document.getElementById("id_descripcion").value = "";
            document.getElementById("modal-title").textContent = "Nueva especialidad";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        formDelModal.addEventListener("submit", function(event) {
            event.preventDefault();
    
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

    
            // Seleccionar todos los inputs, select y textarea
            const seccionEdit = document.getElementById("seccion-edit");
            const allinputsModal = seccionEdit.querySelectorAll(".campo-input input,.campo-input select,.campo-input textarea");
    
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim()) {
                    hayErrores = true;
                    let mensajeError = '';
    
                    // Verifica el campo y muestra un mensaje de error específico
                    if (input.id === 'id_nombre_especialidad') {
                        mensajeError = 'El nombre de la especialidad es obligatorio.';
                    } else if (input.id === 'id_departamento') {
                        mensajeError = 'Por favor, seleccione un departamento.';
                    } else if (input.id === 'id_descripcion') {
                        mensajeError = 'La descripción es obligatoria.';
                    }
    
                    errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                    input.parentElement.appendChild(errorDiv); // Agrega el mensaje de error debajo del campo
                }
            });
    
            if (!hayErrores) {
                formDelModal.submit();
            }
        });
    }

    if (btnNewServicio){
        btnNewServicio.addEventListener("click",() => {
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";
            document.getElementById("id_servicio").value = "";
            document.getElementById("id_nombre_servicio").value = "";
            document.getElementById("id_capacidad_diaria").value = "";
            document.getElementById("id_descripcion").value = "";
            document.getElementById("id_departamento").value = "";

            const checkboxes = document.querySelectorAll('input[name="lugar"]');
            checkboxes.forEach((checkbox) => {
                checkbox.classList.add('selected'); 
                checkbox.checked = false
            });     

            document.getElementById("modal-title").textContent = "Nuevo servicio de diagnostico";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        formDelModal.addEventListener("submit", function(event) {
            event.preventDefault();
    
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

    
            // Seleccionar todos los inputs, select y textarea
            const seccionEdit = document.getElementById("seccion-edit");
            const allinputsModal = seccionEdit.querySelectorAll(".campo-input input,.campo-input select,.campo-input textarea");
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim()) {
                    console.log(input)
                    hayErrores = true;
                    let mensajeError = '';
    
                    // Verifica el campo y muestra un mensaje de error específico
                    if (input.id === 'id_nombre_servicio') {
                        mensajeError = 'El nombre del servicio es obligatorio.';
                    } 
                    else if (input.id === 'id_departamento') {
                        mensajeError = 'Por favor, seleccione un departamento.';
                    }
                    else if (input.id === 'id_descripcion') {
                        mensajeError = 'La descripción es obligatoria.';
                    }
                    else if (input.id === 'id_lugar') {
                        mensajeError = 'Por favor, seleccione por lo menos un lugar.';
                    }
    
                    errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                    input.parentElement.appendChild(errorDiv); 
                }
            });
    
            if (!hayErrores) {
                formDelModal.submit();
            }
        });
    }

    if (btnNewEstudio){
        btnNewEstudio.addEventListener("click",() => {
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";
            document.querySelector(".modal-content").style.width = "fit-content";
            document.getElementById("id_estudio").value = "";
            document.getElementById("id_nombre_estudio").value = "";
            document.getElementById("id_servicio_diagnostico").value = "";
            document.getElementById("id_tipo_resultado").value = "";

            const checkboxes = document.querySelectorAll('input[name="especialidad"]');
            checkboxes.forEach((checkbox) => {
                checkbox.checked = false
            });  

            document.getElementById("modal-title").textContent = "Nuevo estudio de diagnostico";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        formDelModal.addEventListener("submit", function(event) {
            event.preventDefault();
    
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

    
            // Seleccionar todos los inputs, select y textarea
            const seccionEdit = document.getElementById("seccion-edit");
            const allinputsModal = seccionEdit.querySelectorAll(".campo-input input,.campo-input select,.campo-input textarea");
    
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim()) {
                    hayErrores = true;
                    let mensajeError = '';
    
                    // Verifica el campo y muestra un mensaje de error específico
                    if (input.id === 'id_nombre_estudio') {
                        mensajeError = 'El nombre del estudio es obligatorio.';
                    } 
                    else if (input.id === 'id_servicio_diagnostico') {
                        mensajeError = 'Por favor, seleccione un servicio de diagnostico.';
                    }
                    else if (input.id === 'id_especialidad') {
                        mensajeError = 'Por favor, seleccione una especialidad.';
                    }
                    else if (input.id === 'id_tipo_resultado') {
                        mensajeError = 'Por favor, seleccione el tipo de resultado del estudio';
                    }
    
                    errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                    input.parentElement.appendChild(errorDiv);
                }
            });
    
            if (!hayErrores) {
                formDelModal.submit();
            }
        });
    }

    if (btnNewLugar){
        btnNewLugar.addEventListener("click",() => {
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";
            document.getElementById("id_lugar").value = "";
            document.getElementById("id_nombre").value = "";  
            document.getElementById("id_tipo").value = "";
            document.getElementById("id_piso").value = "";
            document.getElementById("id_sala").value = "";
            document.getElementById("id_abreviacion").value = "";
            document.getElementById("id_capacidad").value = "";
            document.getElementById("id_departamento").value = "";
            document.getElementById("id_unidad").value = "";
            document.getElementById("id_descripcion").value = "";
            document.getElementById("id_es_critico").checked = false;
            document.getElementById("id_activo").checked = false;
            document.getElementById("modal-title").textContent = "Nuevo lugar";
            toggleTipoLugar();

            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        formDelModal.addEventListener("submit", function(event) {
            event.preventDefault();
    
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());

    
            // Seleccionar todos los inputs, select y textarea
            const seccionEdit = document.getElementById("seccion-edit");
            const allinputsModal = seccionEdit.querySelectorAll(".campo-input input,.campo-input select,.campo-input textarea");
            const tipoLugar = document.getElementById("id_tipo");
    
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim()) {
                    let mensajeError = '';
            
                    // Campos que siempre son obligatorios
                    if (input.id === 'id_nombre') {
                        mensajeError = 'El nombre del lugar es obligatorio.';
                    } else if (input.id === 'id_tipo') {
                        mensajeError = 'Por favor, seleccione un tipo de lugar.';
                    } else if (input.id === 'id_piso') {
                        mensajeError = 'Por favor, ingrese el n° del piso del lugar.';
                    }
                    // Campos obligatorios solo si no es unidad_atenc
                    else if (tipoLugar.value !== "unidad_atenc") {
                        if (input.id === 'id_sala') {
                            mensajeError = 'Por favor, ingrese el N° sala del lugar';
                        } else if (input.id === 'id_capacidad') {
                            mensajeError = 'Por favor, ingrese la capacidad del lugar.';
                        }
                    }

                    if (mensajeError) {
                        hayErrores = true;
                        errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                        input.parentElement.appendChild(errorDiv);
                    }
                }
            });
    
            if (!hayErrores) {
                formDelModal.submit();
            }
        });
    }

    if (btnPlantillaEstudio){
        btnPlantillaEstudio.addEventListener("click",() => {
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.getElementById("seccion-form-filter").style.display="none"
            document.getElementById("seccion-edit").style.display ="block";

            document.getElementById("id_plantilla").value = "";
            document.getElementById("id_estudio").value = "";
            document.getElementById("id_estructura").value = "";

            document.getElementById("modal-title").textContent = "Nueva plantilla de estudio";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        formDelModal.addEventListener("submit", function(event) {
            event.preventDefault();
    
            // Limpiar errores previos
            document.querySelectorAll('.error-message').forEach(errorDiv => {
                errorDiv.remove();
            });
    
            // Seleccionar todos los inputs, select y textarea
            const seccionEdit = document.getElementById("seccion-edit");
            const allinputsModal = seccionEdit.querySelectorAll(".campo-input input,.campo-input select,.campo-input textarea");
    
            let hayErrores = false;
    
            allinputsModal.forEach(input => {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('error-message');
    
                if (!input.value.trim()) {
                    hayErrores = true;
                    let mensajeError = '';
    
                    // Verifica el campo y muestra un mensaje de error específico
                    if (input.id === 'id_estudio') {
                        mensajeError = 'Por favor, seleccione un estudio.';
                    } 
                    else if (input.id === 'id_estructura') {
                        mensajeError = 'Por favor, ingrese la estructura en formato JSON del estudio';
                    }
                    
                    errorDiv.innerHTML = `<p>${mensajeError}</p>`;
                    input.parentElement.appendChild(errorDiv); 
                }
            });
    
            if (!hayErrores) {
                formDelModal.submit();
            }
        });
    }

    if (btnNewLugarTrabajo){
        btnNewLugarTrabajo.addEventListener("click",() => { 
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.getElementById("modal-title").textContent = "Asignar nuevo lugar de trabajo";
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-lugarTrabajo").style.display ="block";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })

        obtenerDisponibilidadLugar();
        document.getElementById("id_lugar").addEventListener('change', obtenerDisponibilidadLugar);
    }     
    

    if (btnNewAsignacion){
        btnNewAsignacion.addEventListener("click",async () => {
                document.getElementById("id_asignacion").value = "";
                document.getElementById("id_rol_profesional").value = "";
                document.getElementById("label-input-mostrar-dato").style.display = "none";
                document.getElementById("id_input-mostrar-dato").style.display = "none";
                document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
                document.getElementById("modal-title").textContent = "Asignar nuevo rol profesional";
                document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
                document.getElementById("seccion-asignaciones").style.display ="block"
                modal.classList.add("show");
                document.body.style.overflow = "hidden"; 
                document.documentElement.style.overflow = "hidden";

        });

        document.getElementById("id_rol_profesional").addEventListener('change', async () =>{
            const id_rolProfesional = document.getElementById("id_rol_profesional").value
            if(id_rolProfesional){
                const url = new URL(window.location.href);
                url.searchParams.set("id_rol_profesional", id_rolProfesional);
    
                try {
                    const response = await fetch(url, {
                        headers: {
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    });
            
                    if (!response.ok) throw new Error("Error al obtener datos");
            
                    const data = await response.json();

                    document.getElementById("label-input-mostrar-dato").style.display = "block";
                    document.getElementById("id_input-mostrar-dato").style.display = "block";
                    if(data.nombre_especialidad){                    
                        document.getElementById("label-input-mostrar-dato").textContent = "Rol profesional asociado a la especialidad medica de:";
                        document.getElementById("id_input-mostrar-dato").value = data.nombre_especialidad;
                    }
                    else if(data.nombre_servicio){                    
                        document.getElementById("label-input-mostrar-dato").textContent = "Rol profesional asociado al servicio de diagnostico:";
                        document.getElementById("id_input-mostrar-dato").value = data.nombre_servicio;
                    }
    
                } 
                catch (err) {
                    alert("Error al cargar los datos");
                    console.error(err);
                }  
            }
            else{
                document.getElementById("id_input-mostrar-dato").style.display = "none";
            }          
        });


    }

    const tipoUsuario = document.getElementById('id_tipoUsuario');
    const especialidad = document.getElementById('id_especialidad');
    const departamento = document.getElementById('id_departamento');
    const servicio = document.getElementById('id_servicio_diagnostico');
    const boxEspecialidad = document.getElementById("seccion-especialidad");
    const boxServicio = document.getElementById("seccion-servicio_diagnostico");
    const boxDepartamento = document.getElementById("seccion-departamento");
    function toggleFields() {
        if(tipoUsuario && (tipoUsuario.value == 3 || tipoUsuario.value == 4 || tipoUsuario.value == 8 )){ 
            if (especialidad) {
                servicio.value="";
                servicio.disabled = true;
                departamento.value="";
                departamento.disabled = true;
                boxDepartamento.style.display = "none";
                boxServicio.style.display = 'none';
                especialidad.disabled = false;
                boxEspecialidad.style.display = 'block';
            }    
        }
        else if (tipoUsuario && tipoUsuario.value == 5){
            if (servicio) {
                especialidad.value="";
                especialidad.disabled = true;
                boxEspecialidad.style.display = 'none';
                departamento.value="";
                departamento.disabled = true;
                boxDepartamento.style.display = 'none';
                servicio.disabled = false;
                boxServicio.style.display = 'block';
            }
        }
        else if(tipoUsuario && tipoUsuario.value == 7){
            if (departamento) {
                especialidad.value="";
                especialidad.disabled = true;
                boxEspecialidad.style.display = 'none';
                servicio.value="";
                servicio.disabled = true;
                boxServicio.style.display = 'none';
                departamento.disabled = false;
                boxDepartamento.style.display = 'block';
            }
        }
        else{
            if(boxEspecialidad){
                especialidad.value="";
                especialidad.disabled = true;
                boxEspecialidad.style.display = 'none';
                servicio.value="";
                servicio.disabled = true;
                boxServicio.style.display = 'none';
                departamento.value="";
                departamento.disabled = true;
                boxDepartamento.style.display = 'none';
            }         
        }
    }
        
    if (tipoUsuario) {
        tipoUsuario.addEventListener('change', toggleFields);
    }
    if (especialidad) {
        especialidad.addEventListener('change', toggleFields);
    }
    if (servicio) {
        servicio.addEventListener('change', toggleFields);
    }
    if (departamento) {
        departamento.addEventListener('change', toggleFields);
    }
    
    toggleFields(); 

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



    /*  #### Esto es parte de la seccion de "Alta de personal"  ###### */
    const tipoUsuarioSeleccionado = document.getElementById("id_tipoUsuarioForm");
    const boxCampoMatricula = document.querySelector(".box-campo-matricula");
    const inputMatricula = document.getElementById("id_numero_matricula");

    const usuariosConMatricula = [3,4,5,7,8];  /* Medico de consultorio, Enfermero, Apoyo en diagnostico y tratamiento , jefe de enfermeria , medico hospitalario */

    function toggleCampoMatricula(){
        const tipoUsuarioSelect = parseInt(tipoUsuarioSeleccionado.value)

        if(usuariosConMatricula.includes(tipoUsuarioSelect)){
            boxCampoMatricula.style.display="flex";
        }
        else{
            boxCampoMatricula.style.display ="none";
            inputMatricula.value="";
        }
    }

    if(tipoUsuarioSeleccionado){
        toggleCampoMatricula();
        tipoUsuarioSeleccionado.addEventListener("change",toggleCampoMatricula);
    }
    /*  #### Fin parte de la seccion de "Alta de personal"  ###### */

});


/*  #### Esta funcion pertenece a la vista de "Editar Personal"  ###### */
function toggleLugar(id) {
    const boxLugar = document.getElementById("boxLugar-" + id);
    const div = document.getElementById("items-lugar-" + id);
    const icon = document.getElementById("icon-arrow-" + id);

    const estaOculto = div.classList.contains("hidden-linea");

    if (estaOculto) {
        boxLugar.classList.add("visible-box");
        div.classList.remove("hidden-linea");
        div.classList.add("visible-linea");
        icon.classList.add("darVuelta");
    } 
    else {
        boxLugar.classList.remove("visible-box");
        div.classList.add("hidden-linea");
        div.classList.remove("visible-linea");
        icon.classList.remove("darVuelta");
    }
}

async function modalEditarRolProfesional(id) {
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.getElementById("modal-title").textContent = "Editar rol profesional";
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-asignaciones").style.display ="block";
    let urlGetLugarTrabajoORolProfesional = document.getElementById("url-getLugarTrabajoORolProfesional").value

    urlGetLugarTrabajoORolProfesional = new URL(urlGetLugarTrabajoORolProfesional, window.location.origin); // Django da una URL relativa → hay que agregarle el origin para que sea una ruta absoluta

    urlGetLugarTrabajoORolProfesional.searchParams.set("id_rolProfesional", id);
    try {
        const response = await fetch(urlGetLugarTrabajoORolProfesional, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) throw new Error("Error al obtener datos");

        const data = await response.json();        


        document.getElementById("id_asignacion").value = data.id_instancia;
        if(document.getElementById("id_especialidad")){
            document.getElementById("id_especialidad").value = data.id_especialidad;
        }
        if(document.getElementById("id_servicio_diagnostico")){
            document.getElementById("id_servicio_diagnostico").value = data.id_servicio_diagnostico;
        }
        
        modal.classList.add("show");
        document.body.style.overflow = "hidden"; 
        document.documentElement.style.overflow = "hidden";
        
    } 
    catch (err) {
        alert("Error al cargar los datos");
        console.error(err);
    }

}

async function modalEditarLugarTrabajo(id) {
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.getElementById("modal-title").textContent = "Editar lugar de trabajo";
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    let urlGetLugarTrabajoORolProfesional = document.getElementById("url-getLugarTrabajoORolProfesional").value

    urlGetLugarTrabajoORolProfesional = new URL(urlGetLugarTrabajoORolProfesional, window.location.origin); // Django da una URL relativa → hay que agregarle el origin para que sea una ruta absoluta

    urlGetLugarTrabajoORolProfesional.searchParams.set("id_lugarTrabajo", id);
    try {
        const response = await fetch(urlGetLugarTrabajoORolProfesional, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) throw new Error("Error al obtener datos");

        const data = await response.json();    

        if (data.sinTurno){
            document.getElementById("seccion-editarLugarTrabajo").style.display ="block";
        }
        else if(!data.sinTurno && data.fecha && data.estado == "asignado"){
            document.getElementById("seccion-confirmarEditarLugarTrabajo").style.display ="block";
            document.getElementById("id_instancia_solicitud").value = data.id_instancia_solicitud;
            document.getElementById("p-solicitar-edicion-lugarTrabajo").textContent = `La solicitud de edicion del trabajo del usuario en este día, a lo largo de las distintas semanas, se registrará en el sistema, pero solo podrá editarse una vez completado el último turno del médico (${data.fecha}). Al confirmar, no podrá revertir esta acción hasta que haya transcurrido el último turno.`
        }
        else if (!data.sinTurno && data.fecha && data.estado == "desasignado"){
            document.getElementById("seccion-confirmarEditarLugarTrabajo").style.display ="block";
            document.getElementById("p-solicitar-edicion-lugarTrabajo").textContent = `La solicitud de trabajo podrá editarse una vez transcurrida la fecha del último turno programado del médico (${data.fecha}).`
            document.getElementById("btn-confirmar-edicion-lugarTrabajo").style.display="none";
        }
        else if(data.estado == "activa"){
            document.getElementById("seccion-editarLugarTrabajo").style.display ="block"
            document.getElementById("p-editar-lugarTrabajo").textContent = data.mensaje;
            document.getElementById("p-editar-lugarTrabajo").style.display="block";
            document.getElementById("btn-guardar-edicion-lugarTrabajo").style.display="none";
        }
    
        if(data.id_instancia){
            document.getElementById("id_instancia").value = data.id_instancia;
            document.getElementById("id_lugar_edit").value = data.id_lugar;
            document.getElementById("id_jornada_edit").value = data.id_jornada;
            document.getElementById("id_rol_edit").value = data.id_rolProfesionalAsignado;

        }


        modal.classList.add("show");
        document.body.style.overflow = "hidden"; 
        document.documentElement.style.overflow = "hidden";
        
    } 
    catch (err) {
        alert("Error al cargar los datos");
        console.error(err);
    }

}

function modalDesasignarRolProfesional(btn){
    const url = btn.dataset.url; 
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-form-desasignar-rolProfesional").style.display = "block";   
    document.getElementById("modal-title").textContent = "Desasignar Rol Profesional";
    document.getElementById("formDesasignarRolProfesional").action = url;
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";

}

async function modalDesasignarLugarTrabajo(btn){
    const url = btn.dataset.url;
    const id_asignacion = btn.dataset.idAsignacionLugarTrabajo;

    let urlDesasignarLugarTrabajo = new URL(url, window.location.origin); // Django da una URL relativa → hay que agregarle el origin para que sea una ruta absoluta
    urlDesasignarLugarTrabajo.searchParams.set("id_lugarTrabajo", id_asignacion);
    try {
        const response = await fetch(urlDesasignarLugarTrabajo, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) throw new Error("Error al obtener datos");

        const data = await response.json();    

        document.getElementById("btn-confirmar-desasignacion-lugarTrabajo").style.display="block";
        if(data.fecha && data.estado == "asignado"){
            document.getElementById("p-desasignar-lugarTrabajo").textContent = `La desasignación del trabajo del usuario en este día, a lo largo de las distintas semanas, se registrará en el sistema, pero solo podrá eliminarse una vez completado el último turno del médico (${data.fecha}). Al confirmar, no podrá revertir esta acción hasta que haya transcurrido el último turno.`
        }
        else if (data.fecha && data.estado == "desasignado"){
            document.getElementById("p-desasignar-lugarTrabajo").textContent = `La asignación de trabajo podrá eliminarse una vez transcurrida la fecha del último turno programado del médico (${data.fecha}).`
            document.getElementById("btn-confirmar-desasignacion-lugarTrabajo").style.display="none";
        }
        else if (data.estado == "activa"){
            document.getElementById("btn-confirmar-desasignacion-lugarTrabajo").style.display="none";
            document.getElementById("p-desasignar-lugarTrabajo").textContent = data.mensaje;
        }
        else{
            document.getElementById("p-desasignar-lugarTrabajo").textContent = data.mensaje;
        }
        
    } 
    catch (err) {
        alert("Error al cargar los datos");
        console.error(err);
    }   
    
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-form-desasignar-lugarTrabajo").style.display = "block";   
    document.getElementById("modal-title").textContent = "Desasignar Lugar de Trabajo";
    document.getElementById("formDesasignarLugarTrabajo").action = url;
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";

}

/*  #### Fin funcion que pertenece a la vista de "Editar Personal"  ###### */















