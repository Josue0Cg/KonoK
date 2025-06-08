document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modal');
    const closeModal = document.getElementById('closeModal');
    const showLogin = document.getElementById('showLogin');
    const showRegister = document.getElementById('showRegister');
    const formContainer = document.getElementById('formContainer');
    const loginBtn = document.getElementById('loginBtn');

    // Mostrar mod
    loginBtn.addEventListener('click', function(e) {
        e.preventDefault();
        modal.style.display = "flex";
    });

    closeModal.addEventListener('click', function() {
        modal.style.display = "none";
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Cambiar a Registro

    showRegister.addEventListener('click', function(e) {
        e.preventDefault();
        formContainer.style.transform = "translateX(-50%)";
    });

    // Cambiar a Login
    showLogin.addEventListener('click', function(e) {
        e.preventDefault();
        formContainer.style.transform = "translateX(0%)";
    });
});
