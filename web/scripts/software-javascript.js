import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getDatabase, ref, set, get, remove } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-database.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";


// Firebase Configuration
const firebaseConfig = {
//Deleted for obvious reasons
  };
  
  
  
  

// Firebase Initialization
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);



const auth = getAuth();

// Verifique o estado de autenticação quando o script é carregado

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




const popupBackground = document.getElementById("popup");
popupBackground.addEventListener("click", function (event) {
    // Check if the clicked element is the popup background itself
    if (event.target === popupBackground) {
        // If so, close the popup
        popupBackground.style.display = "none";
    }
});

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


// Função para preencher automaticamente os campos do formulário com dados do banco de dados
function fillFormFromDatabase() {
    console.log("Tentando preencher o formulário com dados do banco de dados.");

    const softwareStatusElement = document.getElementById("SoftwareStatus");
    const softwareVersionElement = document.getElementById("SoftwareVersion");

    // Faça a consulta no banco de dados Firebase
    const softwareRef = ref(db, 'software');
    get(softwareRef).then((snapshot) => {
        if (snapshot.exists()) {
            const softwareData = snapshot.val();

            console.log("Dados do banco de dados:", softwareData);
            
            // Atualize os campos do formulário com os dados do banco de dados
            softwareStatusElement.value = softwareData.status;
            softwareVersionElement.value = softwareData.version;

            console.log("Campos do formulário atualizados com sucesso!");
        } else {
            console.log("Dados do banco de dados não encontrados.");
        }
    }).catch((error) => {
        console.error("Erro ao obter dados do banco de dados:", error);
    });
}

// Chame a função para preencher automaticamente os campos do formulário com dados do banco de dados
fillFormFromDatabase();


// Ouvinte de evento para o botão de salvar
document.getElementById("SaveStatus").addEventListener("click", function() {
    saveChangesToDatabase();
});

// Função para salvar as alterações no banco de dados Firebase
function saveChangesToDatabase() {
    const softwareStatusElement = document.getElementById("SoftwareStatus");
    const softwareVersionElement = document.getElementById("SoftwareVersion");

    // Obtenha os valores dos campos do formulário
    const newStatus = softwareStatusElement.value;
    const newVersion = softwareVersionElement.value;

    // Atualize os valores no banco de dados
    const softwareRef = ref(db, 'software');
    set(softwareRef, {
        status: newStatus,
        version: newVersion
    }).then(() => {
        // Exiba uma mensagem de sucesso no popup
        showPopup("Alterações salvas com sucesso!");
    }).catch((error) => {
        // Exiba uma mensagem de erro no popup
        showPopup("Erro ao salvar alterações. Por favor, tente novamente.");
        console.error("Erro ao salvar alterações:", error);
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

