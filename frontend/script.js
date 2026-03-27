

document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('hero-login-button');
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');

    loginButton.addEventListener('click', () => {
        loginForm.classList.toggle('d-none');

        if (!loginForm.classList.contains('d-none')) {
            loginForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
            emailInput.focus();
        }
    });
});
