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
    const loginForm = document.getElementById('auth-form');

    // Preencher os campos de email e senha se os parâmetros forem passados
    const urlParams = new URLSearchParams(window.location.search);
    const emailParam = urlParams.get('email');
    const passwordParam = urlParams.get('password');

    if (emailParam !== null && emailParam !== undefined) {
        document.getElementById('email-input').value = emailParam;
    }
    if (passwordParam !== null && passwordParam !== undefined) {
        document.getElementById('password-input').value = passwordParam;
    }

    loginButton.addEventListener('click', performLogin);



    loginForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Impede a submissão padrão do formulário
        performLogin();
    });

    // Ouvinte de evento para tecla "Enter" no campo de senha
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
    
                // Exibir no console o email e senha inseridos pelo usuário
                console.log(`Email: ${email}`);
                console.log(`Password: ${password}`);
    
                // Verificar se o e-mail foi verificado
                if (user.emailVerified) {
                    if (user.uid === '00000000000000000000000000') {
                        // UID especial para admin, redireciona para admin.html
                        window.location.href = 'admin.html';
                    } else {
                        showNotification('Login successful!', 'alert-success', 'fas fa-check-circle');
    
                        // Redireciona para admin.html diretamente
                        setTimeout(() => {
                            window.location.href = 'admin.html';
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

    // Remove a verificação de parâmetro de versão
    console.log('code715');
});
