import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getDatabase, ref, set, get } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-database.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

// Firebase Configuration
const firebaseConfig = {
//Deleted for obvious reasons
};

// Firebase Initialization
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

function showPopup(message) {
    const popup = document.getElementById("popup");
    const popupMessage = document.getElementById("popup-message");
    const popupClose = document.getElementById("popup-close");

    popupMessage.textContent = message;
    popup.style.display = "flex";

    // Adiciona um evento de clique no botão "Close" para fechar o popup
    popupClose.addEventListener("click", function (event) {
        event.stopPropagation(); // Evita a propagação para o popup principal
        popup.style.display = "none";
    });

    // Adiciona um evento de clique no corpo da página para fechar o popup quando clicar fora dele
    document.body.addEventListener("click", function () {
        popup.style.display = "none";
    });
}




const editorLicense = document.getElementById("btnEdit");
const listLicensesButton = document.getElementById("btnLicenseList");
const massGenerator = document.getElementById("btnMassGenerator");
const userList = document.getElementById("btnUserList");
const userEditor = document.getElementById("btnUserEditor");
const softwareData = document.getElementById("btnSoftware");

editorLicense.addEventListener("click", function () {
    window.location.href = `admin.html`;
});

listLicensesButton.addEventListener("click", function () {
    window.location.href = `listlicense.html`;
});

massGenerator.addEventListener("click", function () {
    window.location.href = `masslist.html`;
});

userList.addEventListener("click", function () {
    window.location.href = `listuser.html`;
});

userEditor.addEventListener("click", function () {
    window.location.href = `users.html`;
});

softwareData.addEventListener("click", function () {
    window.location.href = `software.html`;
});





const auth = getAuth();


// Verifique o estado de autenticação quando o script é carregado
onAuthStateChanged(auth, function(user) {
    if (user) {
        const userEmail = user.email;
        const uid = user.uid;

        // Array de UIDs permitidos
        const allowedUIDs = ["TaFyTUk6OrZL4F60zwA4qNZKXw92", "0AaunbR3vpQWaxleR3BfAPWJ07t1", "bg7CXMCCQOhm2eeYCdHqSrJ4gdD2"];

        // Verifique se o usuário logado tem um UID permitido
        if (!allowedUIDs.includes(uid)) {
            // Se o UID não estiver na lista de UIDs permitidos, redirecione para a página de login
            window.location.href = "login.html";
            return;
        }

        const userNameElement = document.getElementById("UserName");
        
        // Exiba o nome do usuário no local desejado da interface do usuário
        userNameElement.innerHTML = "<strong>User:</strong> " + userEmail;
        userNameElement.style.fontSize = "18px";  // Tamanho da fonte ajustado
        userNameElement.style.fontWeight = "bold"; // Texto em negrito
        userNameElement.style.textShadow = "2px 2px 4px rgba(0, 0, 0, 0.5)";  // Sombra adicionada
    } else {
        // O usuário não está autenticado, redirecione para a página de login
        window.location.href = "login.html";
    }
});








// Função para obter parâmetros da URL
function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

const userIdParam = getURLParameter("userId");

if (userIdParam) {
    const userRef = ref(db, `users/${userIdParam}`);

    get(userRef).then((snapshot) => {
        if (snapshot.exists()) {
            const userData = snapshot.val();

            // Preencha os campos do formulário com os dados do usuário
            document.getElementById("SelectedUserEmail").value = userData.email;
            document.getElementById("UserStatus").value = userData.status;
            document.getElementById("UserHWID").value = userData.hwid;

            // Adicione a linha abaixo para exibir a licença do usuário
            document.getElementById("UserLicense").value = userData.License;

        } else {
            showPopup("User not found.");
        }
    }).catch((error) => {
        showPopup("Error fetching user data: " + error.message);
    });
}



const saveUserInfoButton = document.getElementById("SaveUserInfo");
const resetHWIDButton = document.getElementById("ResetHWID");

// Manipulador de evento para o botão de salvar
saveUserInfoButton.addEventListener("click", function () {
    const userId = getURLParameter("userId");
    const selectedUserEmail = document.getElementById("SelectedUserEmail").value;
    const userStatus = document.getElementById("UserStatus").value;
    const userHWID = document.getElementById("UserHWID").value;
    const userLicense = document.getElementById("UserLicense").value; // Adiciona esta linha para obter a licença

    // Referência ao nó específico do usuário no banco de dados
    const userRef = ref(db, `users/${userId}`);

    // Atualize as informações do usuário no banco de dados
    set(userRef, {
        email: selectedUserEmail,
        status: userStatus,
        hwid: userHWID,
        License: userLicense // Adiciona a licença aos dados do usuário
    }).then(() => {
        showPopup("User information saved successfully.");
    }).catch((error) => {
        showPopup("Error saving user information: " + error.message);
    });
});
// Manipulador de evento para o botão de resetar HWID
resetHWIDButton.addEventListener("click", function () {
    // Limpe o conteúdo da caixa de texto do HWID
    document.getElementById("UserHWID").value = "";

});


