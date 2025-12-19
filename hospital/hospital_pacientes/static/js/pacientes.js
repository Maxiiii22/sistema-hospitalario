const modal = document.getElementById("editModal");
const closeModalBtn = document.getElementById("closeEditModal");
const btnGuardar = document.querySelector(".btn-guardar");
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
    modal.querySelector(".modal-detalles-consulta").style.width = "clamp(310px, 90%, 1100px)";
    document.getElementById("seccion-form-filter").style.display = "none";
    document.getElementById("seccion-edit").style.display = "block";
    document.getElementById("parte-estudios").style.display = "none";
    document.getElementById("parte-medicamentos").style.display = "none";
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
    document.getElementById("modalMedicaciones").innerHTML = btn.dataset.medicaciones;
    document.documentElement.style.overflow = "hidden"; 
    document.body.style.overflow = "hidden";
}


function abrirDetalleEstudios(btn) {
    if(btn.dataset.res){
        btnVolverConsulta.style.display = "none";
    }
    else{
        btnVolverConsulta.style.display = "block";
        btnVolverConsulta.dataset.idConsulta = btn.dataset.idConsulta;
    }
    modal.classList.add("show");
    modal.querySelector(".modal-detalles-consulta").style.width = "clamp(300px, 90%, 1100px)";
    document.getElementById("seccion-form-filter").style.display = "none";
    document.getElementById("seccion-edit").style.display = "block";    
    document.getElementById("parte-consultas").style.display = "none";
    document.getElementById("parte-medicamentos").style.display = "none";
    document.getElementById("parte-estudios").style.display = "block";
    document.getElementById("modal-title").textContent = "Detalles del estudio";
    document.getElementById("textProfesional").textContent = "Solicitado por:";
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden"; 
    document.getElementById("modalProfesional").textContent = btn.dataset.profesional;
    document.getElementById("modalPaciente").textContent = btn.dataset.paciente;
    document.getElementById("modalFecha").textContent = btn.dataset.fecha;
    document.getElementById("modalTipoEstudio").textContent = btn.dataset.tipoEstudio;
    document.getElementById("modalMotivo").innerHTML = btn.dataset.motivo;
    document.getElementById("modalIndicaciones").textContent = btn.dataset.indicaciones;
    document.getElementById("modalEstado").innerHTML = btn.dataset.estado;
}


function abrirDetalleMedicamento(btn) {
    btnVolverConsulta.style.display = "block";
    btnVolverConsulta.dataset.idConsulta = btn.dataset.idConsulta;
    modal.classList.add("show");
    modal.querySelector(".modal-detalles-consulta").style.width = "clamp(300px, 90%, 1100px)";
    document.getElementById("seccion-form-filter").style.display = "none";
    document.getElementById("seccion-edit").style.display = "block";    
    document.getElementById("parte-consultas").style.display = "none";
    document.getElementById("parte-estudios").style.display = "none";
    document.getElementById("parte-medicamentos").style.display = "block";
    document.getElementById("modal-title").textContent = "Detalles del medicamento";
    document.getElementById("textProfesional").textContent = "Recetado por:";
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden"; 
    document.getElementById("modalProfesional").textContent = btn.dataset.profesional;
    document.getElementById("modalPaciente").textContent = btn.dataset.paciente;
    document.getElementById("modalFecha").textContent = btn.dataset.fecha;
    document.getElementById("modalMedicamento").textContent = btn.dataset.medicamento;
    document.getElementById("modalDosis").innerHTML = btn.dataset.dosis;
    document.getElementById("modalFrecuencia").textContent = btn.dataset.frecuencia;
    document.getElementById("modalTiempoUso").textContent = btn.dataset.tiempoUso;
}

function DetalleConsulta(btn){
    let idConsulta = btn.dataset.idConsulta;
    const btnDetalleConsulta = document.getElementById("idConsulta_"+idConsulta);
    abrirDetalle(btnDetalleConsulta);
}

function DetalleEstudio(btn){
    let idOrden = btn.dataset.idOrden;
    const btnDetalleEstudio = document.getElementById("idOrden_"+idOrden);
    abrirDetalleEstudios(btnDetalleEstudio);
}

function DetalleMedicamento(btn){
    let idMedicamento = btn.dataset.idMedicamento;
    const btnDetalleMedicamento = document.getElementById("idMedicamento_"+idMedicamento);
    abrirDetalleMedicamento(btnDetalleMedicamento);
}


let mostrandoFuturos = true;
function toggleTurnos() {
    if (mostrandoFuturos) {
        document.getElementById("titulo").textContent = "Turnos anteriores para consultas médicas";
        document.getElementById("turnos-futuros").style.display = "none";
        document.getElementById("turnos-anteriores").style.display = "block";
        document.getElementById("toggleBtn").textContent = "Ver turnos futuros";
    } else {
        document.getElementById("titulo").textContent = "Turnos futuros para consultas médicas";
        document.getElementById("turnos-futuros").style.display = "block";
        document.getElementById("turnos-anteriores").style.display = "none";
        document.getElementById("toggleBtn").textContent = "Ver turnos anteriores";
    }
    mostrandoFuturos = !mostrandoFuturos;
}

// estudios
let mostrandoEstudiosFuturos = true;
function toggleTurnosEstudios() {
    if (mostrandoEstudiosFuturos) {
        document.getElementById("tituloEstudios").textContent = "Turnos anteriores para estudios";
        document.getElementById("turnosEstudios-futuros").style.display = "none";
        document.getElementById("turnosEstudios-anteriores").style.display = "block";
        document.getElementById("toggleBtn2").textContent = "Ver turnos futuros";
    } else {
        document.getElementById("tituloEstudios").textContent = "Turnos futuros para estudios";
        document.getElementById("turnosEstudios-futuros").style.display = "block";
        document.getElementById("turnosEstudios-anteriores").style.display = "none";
        document.getElementById("toggleBtn2").textContent = "Ver turnos anteriores";
    }
    mostrandoEstudiosFuturos = !mostrandoEstudiosFuturos;
}


// mostrar futuros por defecto
if(document.getElementById("turnos-futuros")){
    document.getElementById("turnos-futuros").style.display = "block";
    document.getElementById("turnos-anteriores").style.display = "none";
    document.getElementById("turnosEstudios-futuros").style.display = "block";
    document.getElementById("turnosEstudios-anteriores").style.display = "none";
}


async function modalReprogramarCita(btn){
    const id_turno = btn.dataset.idTurno; 
    const urlReprogramar = btn.dataset.urlReprogramar; 

    if (id_turno){
        const url = new URL(window.location.href);
        url.searchParams.set("id_turno_medico", id_turno);
        try {
            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });  

            if (!response.ok) throw new Error("Error al obtener datos");
                const data = await response.json()
                document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
                document.getElementById("seccion-reprogramar-turnoMedico").style.display = "block";                             
                document.getElementById("modal-title").textContent = "Reprogramar Cita Médica";
                const btnFormReprogramar= document.querySelector(".btn-form-reprogramar");
                btnFormReprogramar.disable = true;

                document.getElementById("profesional").innerHTML =`<strong>Médico:</strong> ${data.profesional}`;
                document.getElementById("matricula").innerHTML = `<strong>N° Matricula:</strong> ${data.matricula}`;
                document.getElementById("sexo").innerHTML = `<strong>Sexo:</strong> ${data.sexo}`;
                document.getElementById("horario").innerHTML = `<strong>Horario:</strong> ${data.horario}`;
                document.getElementById("lugar").innerHTML =  `<strong>Atención en:</strong> ${data.lugar}</strong>`;
                document.getElementById("fecha_turno").innerHTML =  `<strong>Fecha actual del turno:</strong> ${data.fecha}</strong>`;
                
                let currentDate = new Date();
                let monthOffset = 0;
        
                // Convertir las fechas disponibles a un array de fechas para fácil comparación
                const fechasDisponibles = data.dias_disponibles.flatMap(profesional => 
                    profesional.disponibilidad.map(dia => dia.fecha)
                );

                function crearCalendario(fechas) { // Función para crear el calendario con todos los días del mes
                
                    const nombreMes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                
                    let botonSeleccionado = null;
                
                
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
                
                    for (let i = 0; i < diaDeLaSemanaInicio; i++) {     // Rellenar con días vacíos al principio
                        const diaVacio = document.createElement('button');
                        diaVacio.disabled = true;
                        calendar.appendChild(diaVacio);
                    }
                
                    while (dia <= fechaLimite.getDate()) {  // Mostrar todos los días del mes
                        const botonDia = document.createElement('button');
                        botonDia.type = "button";
                        botonDia.textContent = dia;
                
                        const fechaDia = new Date(fechaInicio.getFullYear(), fechaInicio.getMonth(), dia);
                        const fechaFormateada = fechaDia.toISOString().split('T')[0];  // Obtener la fecha en formato YYYY-MM-DD
                
                        if (fechas.includes(fechaFormateada)) { // Verificar si el día está en la lista de días disponibles
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
                                btnFormReprogramar.disabled = false;
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
                    crearCalendario(fechasDisponibles);
                });
        
                // Función para ir al mes siguiente
                document.getElementById('nextMonth').addEventListener('click', function() {
                    monthOffset++;
                    crearCalendario(fechasDisponibles);
                });
        
                // Inicializar el calendario
                crearCalendario(fechasDisponibles);        
                
                modal.classList.add("show");
                document.body.style.overflow = "hidden"; 
                document.documentElement.style.overflow = "hidden";

                document.getElementById("formReprogramarCitaMedica").action = urlReprogramar;

            }
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }
        }
}

function modalCancelarCita(btn){
    const id_turno = btn.dataset.idTurno; 
    const urlCancelarTurno = btn.dataset.urlCancelarTurno; 
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-form-cancelar-cita-medica").style.display = "block";   
    document.getElementById("modal-title").textContent = "Cancelar Cita Médica";
    document.getElementById("formCancelarCitaMedica").action = urlCancelarTurno;
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}

async function modalReprogramarCitaEstudio(btn){
    const id_turnoEstudio = btn.dataset.idTurnoEstudio; 
    const urlReprogramarEstudio = btn.dataset.urlReprogramarEstudio; 


    if (id_turnoEstudio){
        const url = new URL(window.location.href);
        url.searchParams.set("id_turno_estudio", id_turnoEstudio);
        try {
            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });  

            if (!response.ok) throw new Error("Error al obtener datos");
                const data = await response.json()
                document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
                document.getElementById("seccion-reprogramar-turnoEstudio").style.display = "block"                             
                document.getElementById("modal-title").textContent = "Reprogramar Turno de Estudio"
                const btnFormReprogramar= document.querySelector(".btn-form-reprogramarEstudio");
                btnFormReprogramar.disable = true;

                document.getElementById("fecha_seleccionadaEstudio").value = "";
                document.getElementById("orden").innerHTML = `<strong>N° Orden:</strong> ${data.id_orden}`;
                document.getElementById("estudio").innerHTML = `<strong>Estudio:</strong> ${data.nombre_estudio}`;
                document.getElementById("p-servicio").innerHTML = `<strong>Realizado por:</strong> ${data.nombre_servicio}`;

                if (data.disponible) {
                    document.getElementById("id_lugar").value = data.lugar_id;
                    document.getElementById("p-lugar").innerHTML = `<strong>Lugar:</strong> ${data.lugar_nombre} <br> <strong>(Piso: ${data.lugar_piso} - N° Sala: ${data.lugar_sala})</strong>`;
                    document.getElementById("horario").innerHTML = `<strong>Horario:</strong> ${data.horario}`;
                    document.getElementById("p-fecha_turno").innerHTML =  `<strong>Fecha actual del turno:</strong> ${data.fecha}</strong>`;
                }
                else{
                    document.getElementById("id_lugar").value = "";
                    document.getElementById("p-lugar").textContent = data.mensaje;
                    document.getElementById("p-lugar").classList.add("error-message-main")
                    document.getElementById("horario").textContent = ""; // limpiar horario
                }
                
                let currentDate = new Date();
                let monthOffset = 0;
                
                const fechasDisponibles = data.dias_disponibles.map(d => d.fecha);;
                function crearCalendario(fechas) { // Función para crear el calendario con todos los días del mes
                
                    const nombreMes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                
                    let botonSeleccionado = null;
                
                
                    const calendar = document.getElementById('calendar2');
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
                
                    for (let i = 0; i < diaDeLaSemanaInicio; i++) {     // Rellenar con días vacíos al principio
                        const diaVacio = document.createElement('button');
                        diaVacio.disabled = true;
                        calendar.appendChild(diaVacio);
                    }
                
                    while (dia <= fechaLimite.getDate()) {  // Mostrar todos los días del mes
                        const botonDia = document.createElement('button');
                        botonDia.type = "button";
                        botonDia.textContent = dia;
                
                        const fechaDia = new Date(fechaInicio.getFullYear(), fechaInicio.getMonth(), dia);
                        const fechaFormateada = fechaDia.toISOString().split('T')[0];  // Obtener la fecha en formato YYYY-MM-DD
                
                        if (fechas.includes(fechaFormateada)) { // Verificar si el día está en la lista de días disponibles
                            botonDia.classList.add('valid');
                            botonDia.addEventListener('click', function() {
                                if (botonSeleccionado) {
                                    botonSeleccionado.classList.remove('seleccionado');
                                }
                                const fecha = document.getElementById("fecha_seleccionadaEstudio");
                                const fechaSeleccionada = `${fechaDia.getFullYear()}-${fechaDia.getMonth() + 1}-${fechaDia.getDate()}`;
                                fecha.value = fechaSeleccionada;
                                botonDia.classList.add('seleccionado');
                                botonSeleccionado = botonDia;
                                btnFormReprogramar.disabled = false;
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
                document.getElementById('prevMonth2').addEventListener('click', function() {
                    monthOffset--;
                    crearCalendario(fechasDisponibles);
                });
        
                // Función para ir al mes siguiente
                document.getElementById('nextMonth2').addEventListener('click', function() {
                    monthOffset++;
                    crearCalendario(fechasDisponibles);
                });
        
                // Inicializar el calendario
                crearCalendario(fechasDisponibles);     
                

                modal.classList.add("show");
                document.body.style.overflow = "hidden"; 
                document.documentElement.style.overflow = "hidden";

                document.getElementById("formReprogramarCitaEstudio").action = urlReprogramarEstudio;

            }
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }
        }
}

function modalCancelarCitaEstudio(btn){
    const id_turnoEstudio = btn.dataset.idTurnoEstudio; 
    const urlCancelarTurnoEstudio = btn.dataset.urlCancelarTurnoEstudio; 
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-form-cancelar-cita-estudio").style.display = "block";   
    document.getElementById("modal-title").textContent = "Cancelar Turno del Estudio";
    document.getElementById("formCancelarCitaEstudio").action = urlCancelarTurnoEstudio; ;
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}

async function editarDatosDelMenor(btn) {
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-edit-menor").style.display ="block";
    const id_menor = btn.dataset.idMenor; 

    document.querySelectorAll('.error-message').forEach(errorDiv => {
        errorDiv.remove();
    });                  

    if (id_menor){
        const url = new URL(window.location.href);
        url.searchParams.set("id", id_menor);
        
        document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
        document.getElementById("seccion-edit-menor").style.display ="block"; 
        document.getElementById("modal-title").textContent = "Editar Datos del Menor"


        try {
            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });
    
            if (!response.ok) throw new Error("Error al obtener datos");
    
            const data = await response.json();                

            document.getElementById("id_menor").value = data.id;
            document.getElementById("id_dni").value = data.dni;
            document.getElementById("id_first_name").value = data.nombre;
            document.getElementById("id_last_name").value = data.apellido;
            document.getElementById("id_sexo").value = data.sexo;
            document.getElementById("id_fecha_nacimiento").value = data.fecha_nacimiento;
            document.getElementById("id_parentesco").value = data.parentesco;

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

function cancelarPagoMiCuenta(btn) {
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}

function cancelarPago(btn) {
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-confirmacion").style.display ="block";
    id_menor_persona = btn.dataset.idPacientePersona;
    document.getElementById("id_menor_persona").value = id_menor_persona;
    document.getElementById("modal-title").textContent = "Cancelar Cuotas"
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}

function reescribirMenor(btn) {
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-reescribirMenor").style.display ="block";
    id_menor_persona = btn.dataset.idPacientePersona;
    document.getElementById("id_menor_persona_reescribir").value = id_menor_persona;
    document.getElementById("modal-title").textContent = "Reescribir Menor"
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";
}

function verPassword(btn){
    const inputId = btn.dataset.target;
    const input = document.getElementById(inputId);
    if (input) {
        if (input.type === 'password') {
            input.type = 'text';
            btn.innerHTML = '<i class="hgi hgi-stroke hgi-view"></i>';
        } else {
            input.type = 'password';
            btn.innerHTML = '<i class="hgi hgi-stroke hgi-eye"></i>';
        }
    }
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


    document.querySelectorAll('.box-estudio').forEach(box => {
        box.addEventListener("click", async () => {
            const id_orden = box.dataset.idOrden; 

            const url = new URL(window.location.href);
            url.searchParams.set("id_orden", id_orden);
            try {
                const response = await fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });
        
                if (!response.ok) throw new Error("Error al obtener datos");
        
                const data = await response.json();
    
                const btnFormSacarTurnoEstudio = document.querySelector(".btn-form-sacar-turnoEstudio");
                btnFormSacarTurnoEstudio.disabled = true;
                document.getElementById("fecha_seleccionada").value = "";
                document.getElementById("id_orden").value = data.id_orden;
                document.getElementById("orden").innerHTML = `<strong>N° Orden:</strong> ${data.id_orden}`;
                document.getElementById("estudio").innerHTML = `<strong>Estudio:</strong> ${data.nombre_estudio}`;
                document.getElementById("p-servicio").innerHTML = `<strong>Realizado por:</strong> ${data.nombre_servicio}`;

                if (data.disponible) {
                    document.getElementById("id_lugar").value = data.lugar_id;
                    document.getElementById("id_servicio_diagnostico").value = data.id_servicio;
                    document.getElementById("p-lugar").innerHTML = `<strong>Lugar:</strong> ${data.lugar_nombre} <br> <strong>(Piso: ${data.lugar_piso} - N° Sala: ${data.lugar_sala})</strong>`;
                    document.getElementById("horario").innerHTML = `<strong>Horario:</strong> ${data.horario}`;
                }
                else{
                    document.getElementById("id_lugar").value = "";
                    document.getElementById("id_servicio_diagnostico").value = "";
                    document.getElementById("p-lugar").textContent = data.mensaje;
                    document.getElementById("p-lugar").classList.add("error-message-main")
                    document.getElementById("horario").textContent = ""; // limpiar horario
                }
                
                let currentDate = new Date();
                let monthOffset = 0;
                
                const fechasDisponibles = data.dias_disponibles.map(d => d.fecha);;
                function crearCalendario(fechas) { // Función para crear el calendario con todos los días del mes
                
                    const nombreMes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                
                    let botonSeleccionado = null;
                
                
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
                
                    for (let i = 0; i < diaDeLaSemanaInicio; i++) {     // Rellenar con días vacíos al principio
                        const diaVacio = document.createElement('button');
                        diaVacio.disabled = true;
                        calendar.appendChild(diaVacio);
                    }
                
                    while (dia <= fechaLimite.getDate()) {  // Mostrar todos los días del mes
                        const botonDia = document.createElement('button');
                        botonDia.type = "button";
                        botonDia.textContent = dia;
                
                        const fechaDia = new Date(fechaInicio.getFullYear(), fechaInicio.getMonth(), dia);
                        const fechaFormateada = fechaDia.toISOString().split('T')[0];  // Obtener la fecha en formato YYYY-MM-DD
                
                        if (fechas.includes(fechaFormateada)) { // Verificar si el día está en la lista de días disponibles
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
                                btnFormSacarTurnoEstudio.disabled = false;
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
                    crearCalendario(fechasDisponibles);
                });
        
                // Función para ir al mes siguiente
                document.getElementById('nextMonth').addEventListener('click', function() {
                    monthOffset++;
                    crearCalendario(fechasDisponibles);
                });
        
                // Inicializar el calendario
                crearCalendario(fechasDisponibles);        
                
                modal.classList.add("show");
                document.body.style.overflow = "hidden";
                document.documentElement.style.overflow = "hidden";

                
            } 
            catch (err) {
                alert("Error al cargar los datos");
                console.error(err);
            }
        })
    })

    const boxProfesionales = document.querySelector(".box-cards-profesionales");
    if(boxProfesionales){
        const diasDisponiblesProfesional = JSON.parse(document.getElementById('diasDisponibles').textContent);
        // Almacenar las fechas disponibles por profesional
        const fechasDisponiblesPorProfesional = {};
        diasDisponiblesProfesional.forEach(profesional => {
            fechasDisponiblesPorProfesional[profesional.profesional] = profesional.disponibilidad.map(dia => dia.fecha);
        });
    
        const nombreMes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
    
        const currentDate = new Date();
        const monthOffsetPorProfesional = {};  // Offset por profesional
    
        function crearCalendarioProfesionales(idProfesional) {
            if (!(idProfesional in monthOffsetPorProfesional)) {
                monthOffsetPorProfesional[idProfesional] = 0;
            }
            let offset = monthOffsetPorProfesional[idProfesional];
    
            const calendar = document.getElementById('calendar_' + idProfesional);
            const prevMonthButton = document.querySelector('.prevMonth_' + idProfesional);
            const nextMonthButton = document.querySelector('.nextMonth_' + idProfesional);           
            calendar.innerHTML = '';  // Limpiar el calendario
    
            const fechaInicio = new Date(currentDate);
            fechaInicio.setMonth(currentDate.getMonth() + offset);
            fechaInicio.setDate(1);
    
            const fechaLimite = new Date(fechaInicio);
            fechaLimite.setMonth(fechaInicio.getMonth() + 1);
            fechaLimite.setDate(0);
    
            const mesActual = nombreMes[fechaInicio.getMonth()];
            const header = document.createElement('div');
            header.classList.add('header');
            header.textContent = `${mesActual} ${fechaInicio.getFullYear()}`;
            calendar.appendChild(header);
    
            const diasDeLaSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
            for (let i = 0; i < 7; i++) {
                const diaSemana = document.createElement('div');
                diaSemana.textContent = diasDeLaSemana[i];
                diaSemana.style.fontWeight = 'bold';
                calendar.appendChild(diaSemana);
            }
    
            const diaDeLaSemanaInicio = fechaInicio.getDay();
            let dia = 1;
    
            for (let i = 0; i < diaDeLaSemanaInicio; i++) {
                const diaVacio = document.createElement('button');
                diaVacio.disabled = true;
                calendar.appendChild(diaVacio);
            }
    
            while (dia <= fechaLimite.getDate()) {
                const botonDia = document.createElement('button');
                botonDia.type = "button";
                botonDia.textContent = dia;
    
                const fechaDia = new Date(fechaInicio.getFullYear(), fechaInicio.getMonth(), dia);
                const fechaFormateada = fechaDia.toISOString().split('T')[0];
    
                if (fechasDisponiblesPorProfesional[idProfesional].includes(fechaFormateada)) {
                    botonDia.classList.add('valid');
                    botonDia.addEventListener('click', function() {
                        document.querySelectorAll(`#calendar_${idProfesional} .seleccionado`).forEach(btn => btn.classList.remove('seleccionado'));
                        const inputFecha = document.getElementById("fecha_seleccionada_" + idProfesional);
                        inputFecha.value = fechaFormateada;
                        botonDia.classList.add('seleccionado');
                        const botones = document.querySelectorAll(`.btn-form-seleccionar-profesional`);
                        botones.forEach(btn => {btn.disabled = true; });
                        const btnFormProfesionalSeleccionado = document.getElementById("btn-form-profesional-id_"+idProfesional);
                        btnFormProfesionalSeleccionado.disabled = false;
                    });
                } else {
                    botonDia.disabled = true;
                    botonDia.classList.add('no-seleccionable');
                }
    
                calendar.appendChild(botonDia);
                dia++;
            }
    
            const diaDeLaSemanaFin = fechaLimite.getDay();
            if (diaDeLaSemanaFin !== 6) {
                for (let i = diaDeLaSemanaFin + 1; i < 7; i++) {
                    const diaVacio = document.createElement('button');
                    diaVacio.disabled = true;
                    calendar.appendChild(diaVacio);
                }
            }
    
            // Actualizar botones de navegación
            prevMonthButton.onclick = function () {
                monthOffsetPorProfesional[idProfesional]--;
                crearCalendarioProfesionales(idProfesional);
            };
    
            nextMonthButton.onclick = function () {
                monthOffsetPorProfesional[idProfesional]++;
                crearCalendarioProfesionales(idProfesional);
            };
        }
    
        // Inicializar los calendarios
        diasDisponiblesProfesional.forEach(profesional => {
            crearCalendarioProfesionales(profesional.profesional);
        });
    }

    if (btnFormFilter){
        btnFormFilter.addEventListener("click",() => {  
            btnVolverConsulta.style.display = "none";
            modal.querySelector(".modal-detalles-consulta").style.width = "clamp(300px, 90%, 350px)";
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











