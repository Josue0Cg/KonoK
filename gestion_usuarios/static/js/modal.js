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
        e.preventDefault();

        // Capturar valores
        const username = document.getElementById('registerUsername').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value.trim();
        const confirmPassword = document.getElementById('registerConfirmPassword').value.trim();

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

        // 💡 Llenar hidden
        document.getElementById('recaptchaToken').value = recaptchaResponse;

        const formData = new FormData(registerForm);

        fetch('/usuarios/register/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Ocurrió un error al registrar.');
        });
    });

    function showError(message) {
        registerAlert.style.display = 'block';
        registerAlert.textContent = message;
        registerAlert.classList.remove('alert-success');
        registerAlert.classList.add('alert-error');
    }

    function showSuccess(message) {
        registerAlert.style.display = 'block';
        registerAlert.textContent = message;
        registerAlert.classList.remove('alert-error');
        registerAlert.classList.add('alert-success');
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email.toLowerCase());
    }
});

const loginForm = document.getElementById('loginForm');
const loginAlert = document.getElementById('loginAlert');

loginForm.addEventListener('submit', function(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value.trim();

    if (!email || !password) {
        showLoginError('Todos los campos son obligatorios.');
        return;
    }

    const formData = new FormData(loginForm);

    fetch('/usuarios/login/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showLoginSuccess(data.message);
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showLoginError(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showLoginError('Ocurrió un error al iniciar sesión.');
    });
});

function showLoginError(message) {
    loginAlert.style.display = 'block';
    loginAlert.textContent = message;
    loginAlert.classList.remove('alert-success');
    loginAlert.classList.add('alert-error');
}

function showLoginSuccess(message) {
    loginAlert.style.display = 'block';
    loginAlert.textContent = message;
    loginAlert.classList.remove('alert-error');
    loginAlert.classList.add('alert-success');
}

