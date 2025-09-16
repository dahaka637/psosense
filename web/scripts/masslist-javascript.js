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



// Função para gerar uma única chave de licença aleatória
function generateRandomLicenseKey() {
    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let licenseKey = "";
    for (let i = 0; i < 20; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        licenseKey += characters[randomIndex];
        if (i % 5 === 4 && i !== 19) {
            licenseKey += "-";
        }
    }
    return licenseKey;
}


// Função para gerar e exibir as chaves de licença com base no número selecionado
function generateRandomLicenseKeys() {
    const selectNumberLicenses = document.getElementById("NumberLicenses");
    const numLicenses = parseInt(selectNumberLicenses.value, 10);

    const selectLicenseDuration = document.getElementById("LicenseDurationField");
    const licenseDuration = selectLicenseDuration.options[selectLicenseDuration.selectedIndex].value;

    const licenseList = document.getElementById("licenseList");
    licenseList.innerHTML = "";

    for (let i = 0; i < numLicenses; i++) {
        const licenseID = generateRandomLicenseKey();
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.textContent = licenseID;
        row.appendChild(cell);
        licenseList.appendChild(row);
    }
}

// Adicione um evento de clique ao botão "GenerateLicense" para chamar a função de geração
const generateButton = document.getElementById("GenerateLicense");
generateButton.addEventListener("click", generateRandomLicenseKeys);

// Função para copiar as licenças geradas para a área de transferência
function copyLicensesToClipboard() {
    const licenses = document.querySelectorAll("#licenseList td");
    if (licenses.length === 0) {
        alert("Nenhuma licença gerada para copiar.");
        return;
    }

    const licensesText = Array.from(licenses).map((license) => license.textContent).join("\n");

    // Cria um elemento de texto temporário para copiar as licenças
    const tempTextArea = document.createElement("textarea");
    tempTextArea.value = licensesText;
    document.body.appendChild(tempTextArea);

    // Seleciona e copia o texto no elemento de texto temporário
    tempTextArea.select();
    document.execCommand("copy");
    document.body.removeChild(tempTextArea);

    alert("Licenças copiadas para a área de transferência.");
}

// Adicione um evento de clique ao botão "CopyLicense" para chamar a função de cópia
const copyButton = document.getElementById("CopyLicense");
copyButton.addEventListener("click", copyLicensesToClipboard);

// Adicione um evento de clique ao botão "SaveLicense" para salvar as licenças no Firebase
const saveButton = document.getElementById("SaveLicense");
saveButton.addEventListener("click", function () {
    const licenseList = document.querySelectorAll("#licenseList td");
    const licenseDuration = document.getElementById("LicenseDurationField").value;

    if (licenseList.length === 0) {
        alert("Nenhuma licença gerada para salvar.");
        return;
    }

    // Use apenas uma mensagem de sucesso para informar que as licenças foram salvas
    alert("Licenças salvas com sucesso.");

    licenseList.forEach((license, index) => {
        const licenseID = license.textContent;
        const creationDate = new Date().toLocaleString();

        const newLicenseData = {
            CreationDate: creationDate,
            LicenseDuration: licenseDuration,
            LicenseID: license.textContent,
            licenseActivated: false,
            LicenseExpiration: "" // Inclua LicenseExpiration vazio
        };

        // Use set para definir a nova licença com a chave LicenseID como nome de nó
        set(ref(db, "licenses/" + licenseID), newLicenseData, (error) => {
            if (error) {
                alert(`Erro ao salvar a licença ${licenseID}: ${error.message}`);
            }
        });
    });
});



const editorLicense = document.getElementById("btnEdit");
const listLicensesButton = document.getElementById("btnLicenseList");
const massGenerator = document.getElementById("btnMassGenerator");
const userList = document.getElementById("btnUserList");
const userEditor = document.getElementById("btnUserEditor");

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



