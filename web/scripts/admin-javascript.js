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

let selectedLicenseKey = null; // Variável para rastrear a licença selecionada

const generateButton = document.getElementById("GenerateLicense");

generateButton.addEventListener("click", function () {
    const generatedLicenseKey = generateRandomLicenseKey();
    document.getElementById("LicenseKey").value = generatedLicenseKey;
});

const saveButton = document.getElementById("SaveLicense");
const expirationInput = document.getElementById("LicenseExpiration");
const extraInfo = document.getElementById("ExtraInfo").value;
const licenseDuration = document.getElementById("LicenseDurationField").value;
const licenseKey = document.getElementById("LicenseKey").value;
const licenseExpiration = expirationInput.value;





saveButton.addEventListener("click", function () {
    const expirationInput = document.getElementById("LicenseExpiration");
    const extraInfo = document.getElementById("ExtraInfo").value;
    const licenseDuration = document.getElementById("LicenseDurationField").value;
    const licenseKey = document.getElementById("LicenseKey").value;

    // Use a data de expiração editada
    const licenseExpiration = expirationInput.value;

    // Check if all essential fields are filled
    if (!licenseKey || !licenseDuration) {
        showPopup("Please fill in all essential fields.");
        return;
    }

    const licenseData = {
        LicenseID: licenseKey,
        LicenseExpiration: licenseExpiration,
        ExtraInfo: extraInfo,
        LicenseDuration: licenseDuration,
        CreationDate: new Date().toLocaleString(),
    };

    const licenseRef = ref(db, "licenses/" + licenseKey);

    set(licenseRef, licenseData).then(() => {
        showPopup("License saved successfully!");
    }).catch((error) => {
        showPopup("Error saving the license: " + error.message);
    });
});





const searchButton = document.getElementById("SearchButton");

searchButton.addEventListener("click", function () {
    const searchKey = document.getElementById("SearchLicense").value;
    const licenseRef = ref(db, "licenses/" + searchKey);

    get(licenseRef).then((snapshot) => {
        if (snapshot.exists()) {
            const licenseData = snapshot.val();
            document.getElementById("LicenseKey").value = licenseData.LicenseID;
            expirationInput.value = licenseData.LicenseExpiration;
            document.getElementById("ExtraInfo").value = licenseData.ExtraInfo;

            // Defina o estado do checkbox com base em licenseActivated
            document.getElementById("licenseActivatedToggle").checked = licenseData.licenseActivated === true;

            // Atualize a licença selecionada ao pesquisar
            selectedLicenseKey = searchKey;

            // Exiba a duração da licença no campo LicenseDurationField
            document.getElementById("LicenseDurationField").value = licenseData.LicenseDuration;
        } else {
            showPopup("License key not found.");
        }
    }).catch((error) => {
        showPopup("Error searching for the license: " + error.message);
    });
});


const removeButton = document.getElementById("RemoveLicense");

removeButton.addEventListener("click", function () {
    const licenseKeyToRemove = document.getElementById("LicenseKey").value;

    if (!licenseKeyToRemove) {
        showPopup("Please enter a License Key to remove.");
        return;
    }

    const licenseRefToRemove = ref(db, "licenses/" + licenseKeyToRemove);

    remove(licenseRefToRemove).then(() => {
        showPopup("License removed from the database successfully!");
        // Limpe a licença selecionada após a remoção bem-sucedida
        selectedLicenseKey = null;
        // Limpe os campos de entrada
        document.getElementById("LicenseKey").value = "";
        expirationInput.value = "";
        document.getElementById("ExtraInfo").value = "";

        // Reset the toggle switch to its default state
        document.getElementById("licenseActivatedToggle").checked = false;
        // Limpe também o campo LicenseDurationField
        document.getElementById("LicenseDurationField").value = "";
    }).catch((error) => {
        showPopup("Error removing the license: " + error.message);
    });
});



// Function to generate a random license key in the format "XXXX-XXXXX-XXXXX-XXXXX"
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

const popupBackground = document.getElementById("popup");
popupBackground.addEventListener("click", function (event) {
    // Check if the clicked element is the popup background itself
    if (event.target === popupBackground) {
        // If so, close the popup
        popupBackground.style.display = "none";
    }
});

// Function to display the popup with a message
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

// Função para obter parâmetros da URL
function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Verifique se há um parâmetro 'licenseID' na URL
const licenseIDParam = getURLParameter("licenseID");

if (licenseIDParam) {
    // Se 'licenseID' estiver presente na URL, busque a licença correspondente no Firebase
    const licenseRef = ref(db, `licenses/${licenseIDParam}`);

    get(licenseRef).then((snapshot) => {
        if (snapshot.exists()) {
            const licenseData = snapshot.val();
            // Preencha os campos do formulário com os dados da licença
            document.getElementById("LicenseKey").value = licenseData.LicenseID;
            expirationInput.value = licenseData.LicenseExpiration;
            document.getElementById("ExtraInfo").value = licenseData.ExtraInfo;
            document.getElementById("LicenseDurationField").value = licenseData.LicenseDuration;

            // Defina o estado do checkbox com base em licenseActivated
            document.getElementById("licenseActivatedToggle").checked = licenseData.licenseActivated === true;
        } else {
            showPopup("License key not found.");
        }
    }).catch((error) => {
        showPopup("Error fetching the license: " + error.message);
    });
}



const licenseActivatedToggle = document.getElementById("licenseActivatedToggle");

// Selecione o campo LicenseExpiration
const licenseExpirationField = document.getElementById("LicenseExpiration");

// Adicione um ouvinte de eventos de clique ao switch
licenseActivatedToggle.addEventListener("click", function () {
    // Verifique se o switch está ativado (marcado)
    if (licenseActivatedToggle.checked) {
        // Obtenha o valor selecionado do campo LicenseDurationField
        const selectedDuration = document.getElementById("LicenseDurationField").value;

        // Se a duração for "Lifetime", defina o campo LicenseExpiration como "Lifetime"
        if (selectedDuration === "Lifetime") {
            document.getElementById("LicenseExpiration").value = "Lifetime";
        } else {
            // Caso contrário, continue com o processo normal de cálculo da data de expiração
            // Defina a data atual
            const currentDate = new Date();

            // Se o valor selecionado for "24 hours", adicione 24 horas à data atual
            // Se for "30 days", adicione 30 dias à data atual
            if (selectedDuration === "24 hours") {
                currentDate.setHours(currentDate.getHours() + 24);
            } else if (selectedDuration === "30 days") {
                currentDate.setDate(currentDate.getDate() + 30);
            } else if (selectedDuration === "7 days") {
                currentDate.setDate(currentDate.getDate() + 7);
            }

            // Preencha o campo LicenseExpiration com a data formatada
            const formattedDate = currentDate.toISOString();
            document.getElementById("LicenseExpiration").value = formattedDate.slice(0, 19).replace("T", " ");
        }
    } else {
        // Se o switch for desativado, limpe o campo LicenseExpiration
        document.getElementById("LicenseExpiration").value = "";
    }
});


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
        // psosense@gmail.com and admin@psosense.com

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



// probmeas: não esta salvando a data de expiração quando já ativada..