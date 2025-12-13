document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', () => {
        const inputId = button.dataset.target;
        const input = document.getElementById(inputId);
        if (input) {
            if (input.type === 'password') {
                input.type = 'text';
                button.innerHTML = '<i class="hgi hgi-stroke hgi-view"></i>';
            } else {
                input.type = 'password';
                button.innerHTML = '<i class="hgi hgi-stroke hgi-eye"></i>';
            }
        }
    });
});

function desplegarMenu(){
    const menu = document.getElementById("menu");
    const icon = document.getElementById("icon-arrow");


    if (!menu.classList.contains("visible-box")) {
        menu.classList.add("visible-box");
        menu.classList.remove("hidden-linea");
        icon.classList.add("darVuelta");
    } 
    else {
        menu.classList.add("hidden-linea");
        menu.classList.remove("visible-box");
        icon.classList.remove("darVuelta");
    }
}