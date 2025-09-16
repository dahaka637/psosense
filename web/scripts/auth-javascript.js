import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getAuth, applyActionCode } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

// Firebase Configuration
const firebaseConfig = {
//Deleted for obvious reasons
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode');
    const oobCode = urlParams.get('oobCode');

    if (mode === 'verifyEmail' && oobCode) {
        // Use oobCode to verify the email
        handleEmailVerification(oobCode);
    } else {
        console.error('Invalid verification link.');
    }

    async function handleEmailVerification(oobCode) {
        try {
            // Apply the email verification action
            await applyActionCode(auth, oobCode);

            // Verification successful, you can redirect or display a message
            console.log('Email verification successful.');

        } catch (error) {
            console.error('Email verification error:', error.message);
            console.log('oobCode:', oobCode);

            // Handle errors if necessary
        }
    }
});
