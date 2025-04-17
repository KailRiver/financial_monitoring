document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления формы
    const authCard = document.querySelector('.auth-card');
    if (authCard) {
        authCard.style.opacity = '0';
        authCard.style.transform = 'translateY(20px)';
        authCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        setTimeout(() => {
            authCard.style.opacity = '1';
            authCard.style.transform = 'translateY(0)';
        }, 100);
    }

    // Валидация пароля при регистрации
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');

    if (passwordInput && confirmPasswordInput) {
        function validatePassword() {
            if (passwordInput.value !== confirmPasswordInput.value) {
                confirmPasswordInput.setCustomValidity("Пароли не совпадают");
            } else {
                confirmPasswordInput.setCustomValidity("");
            }
        }

        passwordInput.addEventListener('change', validatePassword);
        confirmPasswordInput.addEventListener('keyup', validatePassword);
    }

    // Показать/скрыть пароль
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.classList.toggle('fa-eye-slash');
        });
    });
});