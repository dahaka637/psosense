import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getDatabase, ref, get, onValue } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-database.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

const firebaseConfig = {
//Deleted for obvious reasons
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

const userList = document.getElementById("userList");
const searchInput = document.getElementById("searchInput");
const userCountSpan = document.getElementById('count');

function populateUserList(users) {
    userCountSpan.textContent = Object.keys(users).length;

    userList.innerHTML = "";

    for (const [userId, user] of Object.entries(users)) {
        const row = document.createElement("tr");

        const userCell = document.createElement("td");
        userCell.id = `user-${userId}`;
        userCell.textContent = user.email;

        // Adiciona um evento de clique ao nome do usuário
        userCell.addEventListener("click", () => {
            // Redireciona para a página edituser.html com o ID do usuário como parâmetro
            window.location.href = `users.html?userId=${userId}`;
        });

        row.appendChild(userCell);

        const statusCell = document.createElement("td");
        statusCell.textContent = user.status;
        row.appendChild(statusCell);

        userList.appendChild(row);
    }
}

function updateUsersCount() {
    const usersRef = ref(db, "users");

    get(usersRef)
        .then((snapshot) => {
            if (snapshot.exists()) {
                const users = snapshot.val();
                userCountSpan.textContent = Object.keys(users).length;
            } else {
                console.log("Nenhum usuário encontrado no banco de dados.");
            }
        })
        .catch((error) => {
            console.error("Erro ao buscar usuários do banco de dados:", error);
        });
}

function fetchUsers() {
    const usersRef = ref(db, "users");

    get(usersRef)
        .then((snapshot) => {
            if (snapshot.exists()) {
                const users = snapshot.val();
                populateUserList(users);
            } else {
                console.log("Nenhum usuário encontrado no banco de dados.");
            }
        })
        .catch((error) => {
            console.error("Erro ao buscar usuários do banco de dados:", error);
        });
}

function filterAndPopulateList(searchTerm) {
    const usersRef = ref(db, "users");

    get(usersRef)
        .then((snapshot) => {
            if (snapshot.exists()) {
                const users = snapshot.val();
                const filteredUsers = filterUsers(users, searchTerm);
                populateUserList(filteredUsers);
            } else {
                console.log("Nenhum usuário encontrado no banco de dados.");
            }
        })
        .catch((error) => {
            console.error("Erro ao buscar usuários do banco de dados:", error);
        });
}

function filterUsers(users, searchTerm) {
    return Object.entries(users).reduce((filtered, [userId, user]) => {
        const userValues = Object.values(user).map(value => String(value).toLowerCase());
        if (userValues.some(value => value.includes(searchTerm))) {
            filtered[userId] = user;
        }
        return filtered;
    }, {});
}

function listenForUserChanges() {
    const usersRef = ref(db, "users");

    onValue(usersRef, (snapshot) => {
        if (snapshot.exists()) {
            const users = snapshot.val();
            populateUserList(users);
            updateUsersCount();
        } else {
            console.log("Nenhum usuário encontrado no banco de dados.");
        }
    }, {
        onlyOnce: false
    });
}

window.addEventListener("load", () => {
    fetchUsers();
    listenForUserChanges();
});

searchInput.addEventListener("input", function () {
    const searchTerm = searchInput.value.trim().toLowerCase();
    filterAndPopulateList(searchTerm);
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



const editorLicense = document.getElementById("btnEdit");
const listLicensesButton = document.getElementById("btnLicenseList");
const massGenerator = document.getElementById("btnMassGenerator");
const userListbtn = document.getElementById("btnUserList");
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

userListbtn.addEventListener("click", function () {
    window.location.href = `listuser.html`;
});

userEditor.addEventListener("click", function () {
    window.location.href = `users.html`;
});

softwareData.addEventListener("click", function () {
    window.location.href = `software.html`;
});

