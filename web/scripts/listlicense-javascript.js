import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getDatabase, ref, get, update } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-database.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

const firebaseConfig = {
//Deleted for obvious reasons
  };

const app = initializeApp(firebaseConfig);
const db = getDatabase();

const licenseList = document.getElementById("licenseList");
const searchInput = document.getElementById("searchInput");
const urlParams = new URLSearchParams(window.location.search);
const authID = urlParams.get("AuthID");


function formatTimeRemaining(expirationDate, currentDate) {
    // Se a data de expiração for "Lifetime", retorne "LIFETIME"
    if (expirationDate === "Lifetime") {
        return "LIFETIME";
    }

    const expirationDateObj = new Date(expirationDate);
    const timeRemaining = expirationDateObj - currentDate;

    // Se a licença não estiver ativada, retorne "🟢 Not Activated"
    if (timeRemaining <= 0) {
        return "🟢 Not Activated";
    }

    const minute = 60 * 1000;
    const hour = minute * 60;
    const day = hour * 24;

    const yearsRemaining = Math.floor(timeRemaining / (day * 365.25));
    const monthsRemaining = Math.floor((timeRemaining % (day * 365.25)) / (day * 30.44));
    const daysRemaining = Math.floor((timeRemaining % (day * 30.44)) / day);
    const hoursRemaining = Math.floor((timeRemaining % day) / hour);
    const minutesRemaining = Math.floor((timeRemaining % hour) / minute);

    let timeRemainingText = "🟢 ";

    // Adicione os elementos ao texto apenas se a quantidade for maior que zero
    if (yearsRemaining > 0) timeRemainingText += `${yearsRemaining} Year `;
    if (monthsRemaining > 0) timeRemainingText += `${monthsRemaining} Month `;
    if (daysRemaining > 0) timeRemainingText += `${daysRemaining} Day `;
    if (hoursRemaining > 0) timeRemainingText += `${hoursRemaining} Hour `;
    if (minutesRemaining > 0) timeRemainingText += `${minutesRemaining} min `;

    return timeRemainingText.trim();
}




async function formatCurrentDate() {
    try {
        const response = await fetch('https://worldtimeapi.org/api/ip');
        const data = await response.json();
        if (data.utc_datetime) {
            const utcDateTime = new Date(data.utc_datetime);
            const options = { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit', 
                timeZone: 'UTC' 
            };
            return utcDateTime.toLocaleString('en-US', options);
        } else {
            console.error('Erro ao obter a data e hora da API UTC');
        }
    } catch (error) {
        console.error('Erro ao obter a data e hora da API UTC', error);
    }
    return 'Erro ao obter a data e hora';
}

async function displayLicenses() {
    const licensesRef = ref(db, "licenses");

    try {
        const snapshot = await get(licensesRef);
        if (snapshot.exists()) {
            const licensesData = snapshot.val();

            licenseList.innerHTML = "";

            // Obtenha a data atual no formato UTC
            const currentDate = new Date(await formatCurrentDate());

            for (const licenseKey in licensesData) {
                const license = licensesData[licenseKey];
                const expirationDate = license.LicenseExpiration;
                const licenseRow = document.createElement("tr");
                licenseRow.dataset.extraInfo = license.ExtraInfo;
                licenseRow.dataset.creationDate = license.CreationDate;
                licenseRow.dataset.product = license.ProductID;

                const licenseCell = document.createElement("td");
                licenseCell.textContent = license.LicenseID;
                licenseRow.appendChild(licenseCell);

                const timeRemainingCell = document.createElement("td");
                if (!expirationDate) {
                    timeRemainingCell.textContent = "⚪ Not Activated";
                } else if (expirationDate === "Lifetime") {
                    timeRemainingCell.textContent = "🟡 Lifetime";
                } else {
                    const expirationDateObj = new Date(expirationDate);
                    if (expirationDateObj < currentDate) {
                        timeRemainingCell.textContent = "🔴 Expired";
                        timeRemainingCell.classList.add("expired");
                    } else {
                        const timeRemainingText = formatTimeRemaining(expirationDate, currentDate);
                        timeRemainingCell.textContent = timeRemainingText;
                    }
                }
                licenseRow.appendChild(timeRemainingCell);

                const typeCell = document.createElement("td");
                typeCell.textContent = license.LicenseDuration;
                licenseRow.appendChild(typeCell);

                const productCell = document.createElement("td");
                productCell.textContent = (license.ProductID === "psosense-basic") ? "Basic" : "Premium";
                licenseRow.appendChild(productCell);

                licenseList.appendChild(licenseRow);
            }
        }
    } catch (error) {
        console.error("Error fetching licenses:", error);
    }
}


function filterList() {
    const searchTerm = searchInput.value.toLowerCase();
    const licenseRows = licenseList.getElementsByTagName("tr");

    for (let i = 0; i < licenseRows.length; i++) {
        const licenseRow = licenseRows[i];
        const licenseCells = licenseRow.getElementsByTagName("td");

        let found = false;

        for (let j = 0; j < licenseCells.length; j++) {
            const cellContent = licenseCells[j].textContent.toLowerCase();

            // Adicione a condição para verificar se o conteúdo da célula contém o termo de pesquisa
            if (cellContent.includes(searchTerm)) {
                found = true;
                break;
            }
        }

        // Se a pesquisa por células não for suficiente, verifique os atributos adicionais
        if (!found) {
            const extraInfo = licenseRow.dataset.extraInfo.toLowerCase();
            const creationDate = licenseRow.dataset.creationDate.toLowerCase();
            const productID = licenseRow.dataset.product.toLowerCase();

            if (extraInfo.includes(searchTerm) || creationDate.includes(searchTerm) || productID.includes(searchTerm)) {
                found = true;
            }
        }

        // Mostre ou oculte a linha com base no resultado da pesquisa
        if (found) {
            licenseRow.style.display = "table-row";
        } else {
            licenseRow.style.display = "none";
        }
    }
}



searchInput.addEventListener("input", filterList);

displayLicenses();



licenseList.addEventListener("click", function (event) {
    const clickedElement = event.target;
    const licenseRow = clickedElement.closest("tr");

    if (clickedElement.classList.contains("edit-icon") || licenseRow) {
        // Se o elemento clicado for o ícone de edição ou uma linha da tabela
        const licenseID = licenseRow.querySelector("td:first-child").textContent;
        console.log("License ID selecionado:", licenseID);

        // Redirecione para a página de edição com parâmetros da licença
        window.location.href = `admin.html?AuthID=${encodeURIComponent(authID)}&licenseID=${encodeURIComponent(licenseID)}`;
    }
});

function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
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



// CHECKBOXES DE HIDE

// Selecione os elementos de checkbox
const hideExpiredCheckbox = document.getElementById("hideexpired");
const hideNoActivedCheckbox = document.getElementById("HideNoActived");
const hideActivedCheckbox = document.getElementById("HideActived");
const hideBasicCheckbox = document.getElementById("HideBasic");
const hideProCheckbox = document.getElementById("HidePro");

// Selecione a tabela que você deseja filtrar
const licenseTable = document.querySelector(".table-container table");

// Função para filtrar a tabela com base nas seleções de checkbox
function filterTable() {
    const rows = licenseTable.querySelectorAll("tbody tr");

    // Obtenha todos os dados de licenças do banco de dados uma vez
    const licensesRef = ref(db, "licenses");
    get(licensesRef).then((snapshot) => {
        if (snapshot.exists()) {
            const licensesData = snapshot.val();

            rows.forEach((row) => {
                const licenseID = row.querySelector("td:first-child").textContent;
                const isExpired = row.querySelector(".expired");

                // Obtenha os dados da licença da coleção local
                const licenseData = licensesData[licenseID];
                if (licenseData) {
                    const expirationDate = licenseData.LicenseExpiration;
                    const productID = licenseData.ProductID;

                    const isActivated = expirationDate !== undefined && expirationDate !== "";

                    const expiredVisible = !hideExpiredCheckbox.checked || !isExpired;
                    const activedVisible = !hideActivedCheckbox.checked || !isActivated;
                    const notActivedVisible = !hideNoActivedCheckbox.checked || (isActivated || isExpired);

                    const basicVisible = !hideBasicCheckbox.checked || !productID.toLowerCase().includes("basic");
                    const proVisible = !hideProCheckbox.checked || !productID.toLowerCase().includes("premium");

                    if (expiredVisible && activedVisible && notActivedVisible && basicVisible && proVisible) {
                        row.style.display = "table-row";
                    } else {
                        row.style.display = "none";
                    }
                }
            });
        }
    });
}



hideExpiredCheckbox.addEventListener("change", filterTable);
hideNoActivedCheckbox.addEventListener("change", filterTable);
hideActivedCheckbox.addEventListener("change", filterTable);

hideBasicCheckbox.addEventListener("change", filterTable);
hideProCheckbox.addEventListener("change", filterTable);


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


document.getElementById("deleteExpiredLicenses").addEventListener("click", async function() {
    const licensesRef = ref(db, "licenses");
    try {
        const snapshot = await get(licensesRef);
        if (snapshot.exists()) {
            const licensesData = snapshot.val();
            const currentDate = new Date(await formatCurrentDate());
            const updates = {}; // Para armazenar as atualizações que excluem as licenças

            for (const licenseID in licensesData) {
                const license = licensesData[licenseID];
                const expirationDate = license.LicenseExpiration;

                if (expirationDate && expirationDate !== "Lifetime") {
                    const expirationDateObj = new Date(expirationDate);
                    if (expirationDateObj < currentDate) {
                        // Se a licença estiver expirada, adicione-a à lista de remoção
                        updates[`licenses/${licenseID}`] = null;
                    }
                }
            }

            if (Object.keys(updates).length > 0) {
                // Remova todas as licenças expiradas do banco de dados
                await update(ref(db), updates);
                showPopup("All expired licenses have been deleted.");
                displayLicenses(); // Atualize a lista de licenças exibidas
            } else {
                showPopup("No expired licenses found.");
            }
        } else {
            showPopup("No licenses found in the database.");
        }
    } catch (error) {
        console.error("Error deleting expired licenses:", error);
        showPopup("Error deleting expired licenses: " + error.message);
    }
});
