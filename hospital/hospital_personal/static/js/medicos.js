const modal = document.getElementById("editModal");
const formDelModal = document.getElementById("editForm");
const closeModalBtn = document.getElementById("closeEditModal");
const btnVolverConsulta = document.querySelector(".btn-volver-consulta");
const btnFormFilter= document.getElementById("btnformFilter");
const form = document.getElementById('filtro-form');

function decodeNewlines(text) {
    return text
        .replace(/\\u000D\\u000A/g, '\n')   // reemplaza \u000D\u000A por salto de línea
        .replace(/\\n/g, '\n')              // reemplaza \n por salto de línea
        .replace(/\\r/g, '\r')              // reemplaza \r si existiera
        .replace(/\\u002D/g, '-')           // reemplaza \u002D por guion
        .replace(/\\u002E/g, '.')           // (opcional) reemplaza \u002E por punto
        .replace(/\\u002C/g, ',');          // (opcional) reemplaza \u002C por coma
}


function abrirDetalle(btn) {
    btnVolverConsulta.dataset.idConsulta = "";
    btnVolverConsulta.style.display = "none";
    modal.classList.add("show");
    modal.querySelector(".modal-detalles-consulta").style.width = "clamp(310px, 95%, 1100px)";
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("parte-consultas").style.display = "block";
    document.getElementById("modal-title").textContent = "Detalles de la consulta";
    document.getElementById("textProfesional").textContent = "Profesional a cargo:";
    document.getElementById("modalPaciente").textContent = btn.dataset.paciente;
    document.getElementById("modalFecha").textContent = btn.dataset.fecha;
    document.getElementById("modalProfesional").textContent = btn.dataset.profesional;
    document.getElementById("modalDiagnostico").textContent = decodeNewlines(btn.dataset.diagnostico);
    document.getElementById("modalObservaciones").textContent = decodeNewlines(btn.dataset.observaciones);
    document.getElementById("modalTratamiento").textContent = decodeNewlines(btn.dataset.tratamiento);
    document.getElementById("modalEstudios").innerHTML = btn.dataset.estudios;
    document.getElementById("modalMedicaciones").innerHTML = decodeNewlines(btn.dataset.medicaciones);
    document.documentElement.style.overflow = "hidden"; 
    document.body.style.overflow = "hidden";
}

function abrirDetalleEstudiosSimple(btn) {
    modal.classList.add("show");
    document.getElementById("parte-medicamentos").style.display = "none";
    document.getElementById("parte-estudios").style.display = "block";
    document.getElementById("modal-title").textContent = "Detalles del estudio";
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden"; 
    document.getElementById("modalTipoEstudio").textContent = btn.dataset.tipoEstudio;
    document.getElementById("modalMotivo").innerHTML = btn.dataset.motivo;
    document.getElementById("modalIndicaciones").textContent = btn.dataset.indicaciones;
    document.getElementById("modalEstado").innerHTML = btn.dataset.estado;
}

function abrirDetalleMedicamentoSimple(btn) {
    modal.classList.add("show");
    document.getElementById("parte-estudios").style.display = "none";
    document.getElementById("parte-medicamentos").style.display = "block";
    document.getElementById("modal-title").textContent = "Detalles del medicamento";
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden"; 
    document.getElementById("modalMedicamento").textContent = btn.dataset.medicamento;
    document.getElementById("modalDosis").innerHTML = btn.dataset.dosis;
    document.getElementById("modalFrecuencia").textContent = btn.dataset.frecuencia;
    document.getElementById("modalTiempoUso").textContent = btn.dataset.tiempoUso;
}


async function abrirDetalleEstudios(idOrden) {
    modal.classList.add("show");
    modal.querySelector(".modal-detalles-consulta").style.width = "clamp(310px, 95%, 1100px)";
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("parte-estudios").style.display = "block";
    document.getElementById("modal-title").textContent = "Detalles del estudio";
    document.getElementById("textProfesional").textContent = "Solicitado por:";

    const url = new URL(window.location.href);
    url.searchParams.set("idOrden", idOrden);

    try {
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });
        if (!response.ok) throw new Error("Error al obtener datos");

        const data = await response.json();     

        btnVolverConsulta.style.display = "block";
        btnVolverConsulta.dataset.idConsulta = data.idConsulta;        
        document.getElementById("modalProfesional").textContent = data.profesional;
        document.getElementById("modalFecha").textContent = data.fecha_solicitud;
        document.getElementById("modalTipoEstudio").textContent = data.tipo_estudio;
        document.getElementById("modalMotivo").innerHTML = data.motivo;
        document.getElementById("modalIndicaciones").textContent = data.motivo;
        document.getElementById("modalEstado").innerHTML = data.estado;
    }
    catch (err) {
        alert("Error al cargar los datos del lugar");
        console.error(err);
    }
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden"; 
}

async function abrirDetalleMedicamento(idMedicamento) {
    modal.classList.add("show");
    modal.querySelector(".modal-detalles-consulta").style.width = "clamp(310px, 95%, 1100px)";
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("parte-medicamentos").style.display = "block";
    document.getElementById("modal-title").textContent = "Detalles del medicamento";
    document.getElementById("textProfesional").textContent = "Recetado por:";

    const url = new URL(window.location.href);
    url.searchParams.set("idMedicamento", idMedicamento);

    try {
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });
        if (!response.ok) throw new Error("Error al obtener datos");

        const data = await response.json();     

        btnVolverConsulta.style.display = "block";
        btnVolverConsulta.dataset.idConsulta = data.idConsulta;        
        document.getElementById("modalProfesional").textContent = data.profesional;
        document.getElementById("modalMedicamento").textContent = data.medicamento;
        document.getElementById("modalDosis").textContent = data.dosis;
        document.getElementById("modalFrecuencia").textContent = data.frecuencia;
        document.getElementById("modalTiempoUso").textContent = data.tiempoUso;
    }    
    catch (err) {
        alert("Error al cargar los datos del lugar");
        console.error(err);
    }
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";    
}

function DetalleConsulta(btn){
    let idConsulta = btn.dataset.idConsulta;
    const btnDetalleConsulta = document.getElementById("idConsulta_"+idConsulta);
    abrirDetalle(btnDetalleConsulta);
}

function DetalleEstudio(btn){
    let idOrden = btn.dataset.idOrden;
    abrirDetalleEstudios(idOrden);
}

function DetalleMedicamento(btn){
    let idMedicamento = btn.dataset.idMedicamento;
    abrirDetalleMedicamento(idMedicamento);
}




function agregarFilaFormset(prefix, tbodySelector) {
    // Ej: prefix = 'estudios' o 'medicaciones'
    const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    const formNum = parseInt(totalFormsInput.value, 10);
    const tbody = document.querySelector(tbodySelector);
    const lastRow = tbody.querySelector('tr:last-child');
    const newRow = lastRow.cloneNode(true);

    // Reemplazar todos los name/id "prefix-<n>-" por el nuevo índice
    const regex = new RegExp(`${prefix}-(\\d+)-`, 'g');

    // Limpia valores y reindexa
    newRow.querySelectorAll('input, select, textarea, label').forEach(el => {
        // Reindexar name
        if (el.name) el.name = el.name.replace(regex, `${prefix}-${formNum}-`);
        // Reindexar id
        if (el.id) el.id = el.id.replace(regex, `${prefix}-${formNum}-`);
        // Reindexar for (labels)
        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(regex, `${prefix}-${formNum}-`);

        // Limpiar valores (excepto opciones <select> sin selección)
        if (el.tagName === 'INPUT') {
            if (el.type === 'checkbox' || el.type === 'radio') {
                el.checked = false;
            } 
            else {
                el.value = '';
            }
        } 
        else if (el.tagName === 'TEXTAREA') {
            el.value = '';
            el.textContent = '';
        }
        else if (el.tagName === 'SELECT') {
            el.selectedIndex = 0; // primera opción (placeholder)
        }
    });
    // Agregar la fila y actualizar el TOTAL_FORMS
    tbody.appendChild(newRow);
    totalFormsInput.value = formNum + 1;
}

async function modalReprogramarCita(btn){
    const id_turno = btn.dataset.idTurno; 
    const urlReprogramarCita = btn.dataset.urlReprogramarCita; 

    if (id_turno){
        const url = new URL(window.location.href);
        url.searchParams.set("id_turno", id_turno);
        try {
            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });  

            if (!response.ok) throw new Error("Error al obtener datos");
                const data = await response.json()
                document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
                document.getElementById("seccion-form-reprogramar-cita").style.display = "block"                 
                const btnReprogramar = document.querySelector(".btn-form-reprogramar");
                btnReprogramar.disabled = true;
                document.getElementById("campo-turno").value = id_turno;
                document.getElementById("modal-title").textContent = "Reprogramar Cita"


                let currentDate = new Date();
                let monthOffset = 0;

                // Convertir las fechas disponibles a un array de fechas para fácil comparación
                const fechasDisponibles = data.dias_disponibles.flatMap(profesional => 
                    profesional.disponibilidad.map(dia => dia.fecha)
                );
            
            
                const nombreMes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio","Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
            
                let botonSeleccionado = null;
            
                // Función para crear el calendario con todos los días del mes
                function crearCalendario() {
                    const calendar = document.getElementById('calendar');
                    calendar.innerHTML = '';  // Limpiar el calendario antes de volver a generarlo
            
                    // Fecha de inicio (primer día del mes)
                    const fechaInicio = new Date(currentDate);
                    fechaInicio.setMonth(currentDate.getMonth() + monthOffset);
                    fechaInicio.setDate(1);
            
                    // Fecha límite (último día del mes)
                    const fechaLimite = new Date(fechaInicio);
                    fechaLimite.setMonth(fechaInicio.getMonth() + 1);
                    fechaLimite.setDate(0);
            
                    // Mostrar el nombre del mes actual
                    const mesActual = nombreMes[fechaInicio.getMonth()];
                    const header = document.createElement('div');
                    header.classList.add('header');
                    header.textContent = `${mesActual} ${fechaInicio.getFullYear()}`;
                    calendar.appendChild(header);
            
                    // Generar celdas para los días de la semana
                    const diasDeLaSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
                    for (let i = 0; i < 7; i++) {
                        const diaSemana = document.createElement('div');
                        diaSemana.textContent = diasDeLaSemana[i];
                        diaSemana.style.fontWeight = 'bold';
                        calendar.appendChild(diaSemana);
                    }
            
                    // Generar los días del mes
                    const diaDeLaSemanaInicio = fechaInicio.getDay();
                    let dia = 1;
            
                    // Rellenar con días vacíos al principio
                    for (let i = 0; i < diaDeLaSemanaInicio; i++) {
                        const diaVacio = document.createElement('button');
                        diaVacio.disabled = true;
                        calendar.appendChild(diaVacio);
                    }
            
                    // Mostrar todos los días del mes
                    while (dia <= fechaLimite.getDate()) {
                        const botonDia = document.createElement('button');
                        botonDia.type = "button";
                        botonDia.textContent = dia;
            
                        const fechaDia = new Date(fechaInicio.getFullYear(), fechaInicio.getMonth(), dia);
                        const fechaFormateada = fechaDia.toISOString().split('T')[0];  // Obtener la fecha en formato YYYY-MM-DD
            
                        // Verificar si el día está en la lista de días disponibles
                        if (fechasDisponibles.includes(fechaFormateada)) {
                            botonDia.classList.add('valid');
                            botonDia.addEventListener('click', function() {
                                if (botonSeleccionado) {
                                    botonSeleccionado.classList.remove('seleccionado');
                                }
                                const fecha = document.getElementById("fecha_seleccionada");
                                const fechaSeleccionada = `${fechaDia.getFullYear()}-${fechaDia.getMonth() + 1}-${fechaDia.getDate()}`;
                                fecha.value = fechaSeleccionada;
                                botonDia.classList.add('seleccionado');
                                botonSeleccionado = botonDia;
                                btnReprogramar.disabled = false;
                            });
                        } 
                        else {
                            botonDia.disabled = true;
                            botonDia.classList.add('no-seleccionable');
                        }
            
                        calendar.appendChild(botonDia);
                        dia++;
                    }
            
                    // Rellenar con días vacíos al final si es necesario
                    const diaDeLaSemanaFin = fechaLimite.getDay();
                    if (diaDeLaSemanaFin !== 6) {
                        for (let i = diaDeLaSemanaFin + 1; i < 7; i++) {
                            const diaVacio = document.createElement('button');
                            diaVacio.disabled = true;
                            calendar.appendChild(diaVacio);
                        }
                    }
                }
            
                // Función para ir al mes anterior
                document.getElementById('prevMonth').addEventListener('click', function() {
                    monthOffset--;
                    crearCalendario();
                });
            
                // Función para ir al mes siguiente
                document.getElementById('nextMonth').addEventListener('click', function() {
                    monthOffset++;
                    crearCalendario();
                });
            
                // Inicializar el calendario
                crearCalendario();        
                    
                document.getElementById("editForm").action = urlReprogramarCita;
                modal.classList.add("show");
                document.body.style.overflow = "hidden"; 
                document.documentElement.style.overflow = "hidden";
                    
            }
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }
        }
}

function modalCancelarCita(btn){
    const id_turno = btn.dataset.idTurno; 
    const urlCancelarCita = btn.dataset.urlCancelarCita; 
    document.getElementById("campo-turno-cancelar").value = id_turno;
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-form-cancelar-cita").style.display = "block";   
    document.getElementById("modal-title").textContent = "Cancelar Cita";
    document.getElementById("formCancelarCita").action = urlCancelarCita;
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
    if (tablaGeneral) {  /* Filtro */
        let timeout = null;

        async function filtrar() {
            clearTimeout(timeout);
            timeout = setTimeout(async () => {
    
                const params = new URLSearchParams(new FormData(form));
                params.append('filtrar', '1');  // Necesario para activar el filtro en la vista
    
                const response = await fetch(`?${params.toString()}`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
    
                const html = await response.text();
                tablaGeneral.innerHTML = html;
    
            }, 300);
        }
    
        form.addEventListener('input', filtrar);
        form.addEventListener('change', filtrar);  // Escuchar cambios que NO disparan input (como el date)
    }

    if (btnFormFilter){
        btnFormFilter.addEventListener("click",() => {  
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













