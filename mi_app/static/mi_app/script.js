function abrirZoom(elemento) {
    const modal = document.getElementById("custom-modal");
    const modalImg = document.getElementById("modal-img");
    modal.style.display = "flex";
    modalImg.src = elemento.src;
}

function cerrarZoom() {
    document.getElementById("custom-modal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("form-consulta");

    if (formulario) {
        formulario.addEventListener("submit", function (event) {

            const nombre = document.getElementById("nombre");
            if (nombre) {
                const nombreValor = nombre.value.trim();
                if (nombreValor === "") {
                    alert("¡Falta información!\nEl campo de Nombre Completo es obligatorio.");
                    nombre.focus();
                    event.preventDefault();
                    return;
                } else if (nombreValor.length < 4) {
                    alert("¡Error en el Nombre!\nPor favor, ingresá tu nombre completo (mínimo 4 caracteres).");
                    nombre.focus();
                    event.preventDefault();
                    return;
                }
            }

            const email = document.getElementById("email");
            if (email) {
                const emailValor = email.value.trim();
                const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

                if (emailValor === "") {
                    alert("¡Falta información!\nEl Correo Electrónico es obligatorio.");
                    email.focus();
                    event.preventDefault();
                    return;
                } else if (!regexEmail.test(emailValor)) {
                    alert("¡Formato Inválido!\nPor favor, ingresá una dirección de correo válida (ejemplo@correo.com).");
                    email.focus();
                    event.preventDefault();
                    return;
                }
            }

            const mensaje = document.getElementById("mensaje");
            if (mensaje) {
                const mensajeValor = mensaje.value.trim();
                if (mensajeValor === "") {
                    alert("¡Falta información!\nEl campo de mensaje no puede estar vacío.");
                    mensaje.focus();
                    event.preventDefault();
                    return;
                } else if (mensajeValor.length < 10) {
                    alert("¡Mensaje muy corto!\nPor favor, escribí al menos 10 caracteres explicativos.");
                    mensaje.focus();
                    event.preventDefault();
                    return;
                }
            }
        });
    }

});