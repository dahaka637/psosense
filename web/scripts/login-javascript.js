import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";


// Firebase Configuration
const firebaseConfig = {
//Deleted for obvious reasons
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

function showNotification(message, className, iconClass) {
    const alertMessage = document.getElementById('alert-message');
    alertMessage.innerHTML = `<i class="${iconClass}"></i>${message}`;
    alertMessage.className = `alert ${className}`;
    alertMessage.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('login-button');
    const signupButton = document.getElementById('signup-button');
    const loginForm = document.getElementById('auth-form');

    // Obter os parâmetros de consulta do URL
    const urlParams = new URLSearchParams(window.location.search);
    const emailParam = urlParams.get('email');
    const passwordParam = urlParams.get('password');

    // Preencher os campos de email e senha se os parâmetros não forem null ou undefined
    if (emailParam !== null && emailParam !== undefined) {
        document.getElementById('email-input').value = emailParam;
    }
    if (passwordParam !== null && passwordParam !== undefined) {
        document.getElementById('password-input').value = passwordParam;
    }

    loginButton.addEventListener('click', performLogin);

    // Adicione um ouvinte de evento para o botão de cadastro
    signupButton.addEventListener('click', () => {
        const currentUrl = new URL(window.location.href);
        window.location.href = `register.html${currentUrl.search}`;
    });

    loginForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Impede a submissão padrão do formulário
        performLogin();
    });

    // Adicione um ouvinte de evento para a tecla "Enter" no campo de senha
    document.getElementById('password-input').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            performLogin();
        }
    });

    function performLogin() {
        const email = document.getElementById('email-input').value;
        const password = document.getElementById('password-input').value;
    
        signInWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                const user = userCredential.user;
    
                console.log(`Email:${email}`);
                console.log(`Password:${password}`);
    
                if (user.emailVerified) {
                    if (user.uid === '00000000000000000000000000') {
                        window.location.href = 'admin.html';
                    } else {
                        showNotification('Login successful!', 'alert-success', 'fas fa-check-circle');
    
                        const hwid = urlParams.get('hwid');
                        const version = urlParams.get('version');
    
                        const redirectUrl = `panel.html?hwid=${hwid}&version=${version}`;
                        setTimeout(() => {
                            window.location.href = redirectUrl;
                        }, 2000);
                    }
                } else {
                    showNotification('Login failed. Email not verified.', 'alert-error', 'fas fa-exclamation-circle');
                }
            })
            .catch((error) => {
                showNotification('Login failed', 'alert-error', 'fas fa-exclamation-circle');
            });
    }

    // Auto login se email e senha forem fornecidos via URL
    if (emailParam && passwordParam) {
        performLogin();
    }

    // Validação da versão de segurança
    const securityParam = urlParams.get('version');
    if (securityParam !== '4.5') {
        console.log('code507');
        window.location.href = 'error.html';
    } else {
        console.log('code715');
    }

});
