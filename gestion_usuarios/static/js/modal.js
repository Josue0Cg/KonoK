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

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const registerAlert = document.getElementById('registerAlert');

    registerForm.addEventListener('submit', function(e) {
        e.preventDefault(); // 🚫 Detener el submit por defecto

        // Capturar valores
        const username = document.getElementById('registerUsername').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value.trim();
        const confirmPassword = document.getElementById('registerConfirmPassword').value.trim();

        // Validaciones
        if (!username || !email || !password || !confirmPassword) {
            showError('Todos los campos son obligatorios.');
            return;
        }

        if (!validateEmail(email)) {
            showError('El correo no es válido.');
            return;
        }

        if (password !== confirmPassword) {
            showError('Las contraseñas no coinciden.');
            return;
        }

        const recaptchaResponse = grecaptcha.getResponse();
        if (recaptchaResponse.length === 0) {
            showError('Por favor verifica que no eres un robot.');
            return;
        }

        // 💡 Llenar el hidden field manualmente
        document.getElementById('recaptchaToken').value = recaptchaResponse;

        // ✅ Ahora sí enviamos el formulario
        registerForm.submit();
    });

    function showError(message) {
        registerAlert.style.display = 'block';
        registerAlert.textContent = message;
        registerAlert.classList.add('alert-error');
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email.toLowerCase());
    } 
});
