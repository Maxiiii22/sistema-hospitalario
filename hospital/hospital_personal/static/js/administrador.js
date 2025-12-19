const modal = document.getElementById("editModal");
const formDelModal = document.getElementById("editForm");
const closeModalBtn = document.getElementById("closeEditModal");
const btnGuardar = document.querySelector(".btn-guardar");
const btnFormFilter= document.getElementById("btnformFilter");
const form = document.getElementById('filtro-form');



async function modalReprogramarCita(btn){
    const id_turno = btn.dataset.idTurno; 

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
                document.getElementById("modal-title").textContent = "Reprogramar cita"


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
    document.getElementById("campo-turno-cancelar").value = id_turno;
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-form-cancelar-cita").style.display = "block";   
    document.getElementById("modal-title").textContent = "Cancelar cita"
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; 
    document.documentElement.style.overflow = "hidden";

}

async function detallesSolicitud(btn){
    const id_solicitud = btn.dataset.idSolicitud; 
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-detalles-solicitud").style.display = "block";   
    document.getElementById("modal-title").textContent = "Detalles de la solicitud"
    modal.querySelector(".modal-content").style.width = "clamp(320px, 90%, 800px)";

    if(id_solicitud){
        const url = new URL(window.location.href);
        url.searchParams.set("id_solicitud", id_solicitud);    
        try {
            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });  

            if (!response.ok) throw new Error("Error al obtener datos");

            const data = await response.json();
            document.getElementById("id_solicitud").value=data.id_solicitud
            const dni = document.getElementById("id_dni").textContent = data.dni;
            const dni_coincidencia = document.getElementById("id_dni-coincidencia").textContent = data.paciente.dni;
            if (dni === dni_coincidencia){
                document.getElementById("coincidencia-dni").innerHTML = `<i class="hgi hgi-stroke hgi-checkmark-circle-01 icon-check"></i>`
            }
            else{
                document.getElementById("coincidencia-dni").innerHTML = `<i class="hgi hgi-stroke hgi-cancel-circle icon-cross"></i>`
            }

            const nombre = document.getElementById("id_nombre").textContent = data.nombre;
            const nombre_coincidencia = document.getElementById("id_nombre-coincidencia").textContent = data.paciente.nombre;
            if (nombre === nombre_coincidencia){
                document.getElementById("coincidencia-nombre").innerHTML = `<i class="hgi hgi-stroke hgi-checkmark-circle-01 icon-check"></i>`
            }
            else{
                document.getElementById("coincidencia-apellido").innerHTML = `<i class="hgi hgi-stroke hgi-cancel-circle" icon-cross></i>`
            }
            
            const apellido = document.getElementById("id_apellido").textContent = data.apellido;
            const apellido_coincidencia = document.getElementById("id_apellido-coincidencia").textContent = data.paciente.apellido;
            if (apellido === apellido_coincidencia){
                document.getElementById("coincidencia-apellido").innerHTML = `<i class="hgi hgi-stroke hgi-checkmark-circle-01 icon-check"></i>`
            }
            else{
                document.getElementById("coincidencia-apellido").innerHTML = `<i class="hgi hgi-stroke hgi-cancel-circle icon-cross"></i>`
            }

            const fecha_nacimiento = document.getElementById("id_fecha_nacimiento").textContent = data.nacimiento;
            const fecha_nacimiento_coincidencia = document.getElementById("id_fecha_nacimiento-coincidencia").textContent = data.paciente.fecha_nacimiento;
            if (fecha_nacimiento === fecha_nacimiento_coincidencia){
                document.getElementById("coincidencia-fecha_nacimiento").innerHTML = `<i class="hgi hgi-stroke hgi-checkmark-circle-01 icon-check"></i>`
            }
            else{
                document.getElementById("coincidencia-fecha_nacimiento").innerHTML = `<i class="hgi hgi-stroke hgi-cancel-circle icon-cross"></i>`
            }

            const email = document.getElementById("id_email").textContent = data.email;
            const email_coincidencia = document.getElementById("id_email-coincidencia").textContent = data.paciente.email;
            if (email === email_coincidencia){
                document.getElementById("coincidencia-email").innerHTML = `<i class="hgi hgi-stroke hgi-checkmark-circle-01 icon-check"></i>`
            }
            else{
                document.getElementById("coincidencia-email").innerHTML = `<i class="hgi hgi-stroke hgi-cancel-circle icon-cross"></i>`
            }

            const telefono = document.getElementById("id_telefono").textContent = data.telefono;
            const telefono_coincidencia = document.getElementById("id_telefono-coincidencia").textContent = data.paciente.telefono;
            if (telefono === telefono_coincidencia){
                document.getElementById("coincidencia-telefono").innerHTML = `<i class="hgi hgi-stroke hgi-checkmark-circle-01 icon-check"></i>`
            }
            else{
                document.getElementById("coincidencia-telefono").innerHTML = `<i class="hgi hgi-stroke hgi-cancel-circle icon-cross"></i>`
            }

            const numero_paciente = document.getElementById("id_numero_paciente").textContent = data.numero_paciente;
            const numero_paciente_coincidencia = document.getElementById("id_numero_paciente-coincidencia").textContent = data.paciente.numero_paciente;
            if (numero_paciente === numero_paciente_coincidencia){
                document.getElementById("coincidencia-numero_paciente").innerHTML = `<i class="hgi hgi-stroke hgi-checkmark-circle-01 icon-check"></i>`
            }
            else{
                document.getElementById("coincidencia-numero_paciente").innerHTML = `<i class="hgi hgi-stroke hgi-cancel-circle icon-cross"></i>`
            }

            document.getElementById("id_observaciones").value = data.observaciones;

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

    if (btnFormFilter){
        btnFormFilter.addEventListener("click",() => {  
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            modal.querySelector(".modal-content").style.width = "";
            
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






















