document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById("hero-login-button");      // hero section button
    const registerButton = document.getElementById("hero-register-button"); // hero section button
    const loginForm = document.getElementById("login-form");               // login form
    const registerForm = document.getElementById("register-form");         // register form

    // show/hide forms
    loginButton.addEventListener('click', () => {
        loginForm.classList.toggle('d-none');
        registerForm.classList.add('d-none'); // hide register
    });

    registerButton.addEventListener('click', () => {
        registerForm.classList.toggle('d-none');
        loginForm.classList.add('d-none');    // hide login
    });

    // submit registration form
    registerForm.addEventListener('submit', (event) => {
        event.preventDefault(); // prevent page reload

        const name = document.getElementById("name-register").value;
        const email = document.getElementById("email-register").value;
        const password = document.getElementById("password-register").value;

        fetch("http://127.0.0.1:8000/register", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name, email, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message); // or display message under the form
                registerForm.reset(); // clear form after success
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // submit login form
    loginForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const email = document.getElementById("email-login").value;
        const password = document.getElementById("password-login").value;

        fetch("http://127.0.0.1:8000/login", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success){
                window.location.href = "home.html";
            }
            else {
                 alert(data.message);
            }
           
            
        })
        .catch(error => {
            console.error('Login error:', error);
            alert('Something went wrong while logging in.');
        });
    });

});
