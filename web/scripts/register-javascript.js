import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, sendEmailVerification  } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

// Firebase Configuration
const firebaseConfig = {
//Deleted for obvious reasons
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

document.addEventListener('DOMContentLoaded', () => {
    const registerButton = document.getElementById('register-button');
    const loginButton = document.getElementById('login-button');

    const registerForm = document.getElementById('auth-form');
    const params = new URLSearchParams(window.location.search);

    registerButton.addEventListener('click', performRegistration);

    loginButton.addEventListener('click', () => {
        const loginURL = 'login.html';

        // Verifica se há parâmetros na URL
        if (params.toString() !== '') {
            window.location.href = `${loginURL}?${params.toString()}`;
        } else {
            window.location.href = loginURL;
        }
    });

    registerForm.addEventListener('submit', (event) => {
        event.preventDefault();
        performRegistration();
    });

    async function performRegistration() {
        const email = document.getElementById('email-input').value;
        const confirmEmail = document.getElementById('confirm-email-input').value;
        const password = document.getElementById('password-input').value;
        const confirmPassword = document.getElementById('confirm-password-input').value;
    
        if (email !== confirmEmail) {
            showNotification(' Emails do not match.', 'alert-error', 'fas fa-exclamation-circle');
            return;
        }
    
        if (password !== confirmPassword) {
            showNotification(' Passwords do not match.', 'alert-error', 'fas fa-exclamation-circle');
            return;
        }
    
        try {
            // Criar usuário
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    
            // Enviar e-mail de verificação
            await sendEmailVerification(userCredential.user, {
                url: 'https://psosense.web.app/auth.html',
                handleCodeInApp: true,
            });
    
            showNotification('Verification email sent! Check your inbox.', 'alert-success', 'fas fa-check-circle');
    
        } catch (error) {
            showNotification(` Registration error: ${error.message}`, 'alert-error', 'fas fa-exclamation-circle');
        }
    }
    

    function showNotification(message, className, iconClass) {
        const alertMessage = document.getElementById('alert-message');
        alertMessage.innerHTML = `<i class="${iconClass}"></i>${message}`;
        alertMessage.className = `alert ${className}`;
        alertMessage.style.display = 'block';
    }

    const passwordInput = document.getElementById('password-input');
    const passwordStrengthBar = document.getElementById('password-strength-bar');

    passwordInput.addEventListener('input', updatePasswordStrength);
    passwordInput.addEventListener('keyup', updatePasswordStrength);

    function calculatePasswordStrength(password) {
        const length = password.length;
        const hasLetters = /[a-zA-Z]/.test(password);
        const hasNumbers = /\d/.test(password);
    
        if (length === 0) {
            return 'none'; // If the password field is empty, consider it as 0%
        } else if (length >= 6 && hasLetters && hasNumbers) {
            return 'strong';
        } else if (length >= 6 && (hasLetters || hasNumbers)) {
            return 'medium';
        } else {
            return 'weak';
        }
    }

    function updatePasswordStrength() {
        const passwordValue = passwordInput.value.trim();
        const passwordStrength = calculatePasswordStrength(passwordValue);

        updatePasswordStrengthBar(passwordStrength);
    }

    function updatePasswordStrengthBar(strength) {
        const colorMap = {
            strong: '#4caf50',
            medium: '#ffc107',
            weak: '#f44336',
            none: 'rgba(68, 68, 68, 0.8)' // Set a default value for 'none'
        };
    
        const widthMap = {
            strong: '100%',
            medium: '50%',
            weak: '25%',
            none: '0%'
        };
    
        passwordStrengthBar.style.width = widthMap[strength];
        passwordStrengthBar.style.backgroundColor = colorMap[strength];
    }

});
