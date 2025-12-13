const modal = document.getElementById("editModal");
const formDelModal = document.getElementById("editForm");
const closeModalBtn = document.getElementById("closeEditModal");
const btnGuardar = document.querySelector(".btn-guardar");
const btnFormFilter= document.getElementById("btnformFilter");
const btnNewNota = document.getElementById("btnNewNota");
const form = document.getElementById('filtro-form');

async function abrirModalDetalleObservacion(btn) {
    document.querySelector(".error-message-main")?.remove()
    document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
    document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
    document.getElementById("seccion-detalles-nota").style.display = "block" 
    let id_observacion = btn.dataset.idObservacionEnfermero;
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
            document.getElementById("id_observaciones-detalles").value = data.observacion;
            document.getElementById("id_signos_vitales-detalles").value = data.signos_vitales;
            document.getElementById("id_procedimientos_realizados-detalles").value = data.procedimientos_realizados;
            document.getElementById("id_medicacion_administrada-detalles").value = data.medicacion_administrada;

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

    if (btnFormFilter){
        btnFormFilter.addEventListener("click",() => {  
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            const sff = document.getElementById("seccion-form-filter");
            if(sff){
                sff.style.display = "block" ;
            }
            document.getElementById("modal-title").textContent = "Buscar por";
            modal.classList.add("show");
            document.body.style.overflow = "hidden"; 
            document.documentElement.style.overflow = "hidden";
        })
    }


    if (btnNewNota){
        btnNewNota.addEventListener("click",async () => { 
            document.querySelector(".error-message-main")?.remove()
            document.querySelectorAll(".error-message").forEach(elemento => elemento.remove());
            document.getElementById("modal-title").textContent = "Nueva Nota";
            document.querySelectorAll(".seccionesDelForm").forEach(elemento => elemento.style.display="none");
            document.getElementById("seccion-new-nota").style.display = "block";           
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

