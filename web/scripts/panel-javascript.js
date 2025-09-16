import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";
import { getDatabase, ref, set, get, remove } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-database.js";

// Firebase Configuration
const firebaseConfig = {
//Deleted for obvious reasons
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getDatabase(app);

const alertQueue = [];

function showNotification(message, className, iconClass) {
    const alertMessage = document.getElementById('alert-message');
    alertMessage.innerHTML = `<i class="${iconClass}"></i>${message}`;
    alertMessage.className = `alert ${className}`;
    alertMessage.style.animation = 'fade-in 0.7s ease-in-out';
    alertMessage.style.display = 'block';

    alertQueue.push(alertMessage);

    setTimeout(() => {
        alertMessage.style.animation = 'fade-out 2.5s forwards';
        setTimeout(() => {
            alertQueue.shift();
            if (alertQueue.length > 0) {
                showNextAlert();
            }
        }, 700);
    }, 4000);

    // Se não houver outros alertas sendo exibidos, inicia o processo de exibição
    if (alertQueue.length === 1) {
        showNextAlert();
    }
}

function showNextAlert() {
    const currentAlert = alertQueue[0];
    currentAlert.style.animation = 'fade-in 0.5s ease-in-out';
    currentAlert.style.display = 'block';
}




const softwareStatusElement = document.getElementById('software-status');
const softwareVersionElement = document.getElementById('software-version');
const hwidStatusElement = document.getElementById('hwid-status');
const softwareStatusIconElement = softwareStatusElement.nextElementSibling.querySelector('i');
const loaderVersionElement = document.getElementById('loader-version');
const userEmailElement = document.getElementById('user-email');
const loadingElement = document.getElementById('loading');
const launchButton = document.getElementById('launch-button')


let accountStatus = false;
let loaderStatus = false;
let softwareStatus = false;
let hwidStatus = false;
let licenseTimeLeft = false;



// Função para deletar a licença do usuário
function deleteLicense(userRef) {
    remove(userRef).then(() => {
        console.log('Licença removida com sucesso do usuário.');
        location.reload();
        // Você pode adicionar mais ações aqui, se necessário
    }).catch((error) => {
        console.error('Erro ao remover a licença do usuário:', error);
    });
}


function updateGlobalStatus(userData, softwareData, urlParams, currentHwid, remainingTotalSeconds) {
    // Lógica para definir as variáveis globais
    accountStatus = (userData.status === 'Active');
    softwareStatus = (softwareData.status === 'Updated');
    loaderStatus = (urlParams.version && urlParams.version === softwareData.version);
    hwidStatus = (currentHwid && currentHwid === userData.hwid);
    licenseTimeLeft = (remainingTotalSeconds > 0);

    // Adicione instruções console.log para imprimir a situação de cada variável global
    console.log('Account Status:', accountStatus);
    console.log('Software Status:', softwareStatus);
    console.log('Loader Status:', loaderStatus);
    console.log('HWID Status:', hwidStatus);
    console.log('timeleft:', remainingTotalSeconds);
    console.log('Time Left Status:', licenseTimeLeft);


    // Chamada da função para atualizar a cor do user-license
    updateLicenseColor();

    // Se licenseTimeLeft for falso, chame a função para remover a licença do usuário
    if (!licenseTimeLeft) {
        deleteLicense(userRef); // Certifique-se de que userRef esteja disponível no escopo
    }

}




function updateLicenseColor() {
    // Adicione esta linha para obter o elemento do HTML onde a licença é exibida
    const userLicenseElement = document.getElementById('user-license');

    // Se licenseTimeLeft for falso, defina a cor como amarelo; caso contrário, defina a cor como verde (ou qualquer outra cor desejada)
    userLicenseElement.style.color = !licenseTimeLeft ? 'yellow' : '#4CAF50';
}




// Função para obter parâmetros de consulta do URL
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const hwid = params.get('hwid');
    const version = params.get('version');
    return { hwid, version };
}



function validateAndLaunch() {
    let errorMessage = '';

    // Verificar quais condições não são verdadeiras
    if (!accountStatus) {
        errorMessage = 'Account is disabled or expired.';
    } else if (!loaderStatus) {
        errorMessage = 'Loader version is outdated.';
    } else if (!softwareStatus) {
        errorMessage = 'Software version is outdated.';
    } else if (!hwidStatus) {
        errorMessage = 'HWID does not match.';
    } else if (!licenseTimeLeft) {
        errorMessage = 'License has expired.';
    }

    // Exibir a mensagem de erro se houver uma
    if (errorMessage) {
        showNotification(` Failed: ${errorMessage}`, 'alert-warning', 'fas fa-exclamation-circle');
    } else {
        // Se todas as condições forem atendidas, mostrar o carregamento
        console.log('Validation_Status: success');

        showNotification(` Success! Open Pro Soccer Online to get started`, 'alert-success', 'fas fa-check-circle');
        loadingElement.style.display = 'inline-block';
        setTimeout(() => {
            loadingElement.style.display = 'none';
        }, 9999999);
    }
}




let userRef; 

// Adicionar evento de clique ao botão
launchButton.addEventListener('click', validateAndLaunch);


document.addEventListener('DOMContentLoaded', () => {
    // Obter parâmetros de consulta do URL
    const urlParams = getUrlParams();

    onAuthStateChanged(auth, (user) => {
        if (user) {
            userEmailElement.textContent = user.email;

            // Definir userRef fora do bloco de função para ser acessível globalmente
            userRef = ref(db, `users/${user.uid}`);

            get(userRef).then((snapshot) => {
                if (snapshot.exists()) {
                    const userData = snapshot.val();
                    console.log('Informações do usuário:', userData);
                    console.log('EmailUsuario:', userData.email);

                    const userLicenseElement = document.getElementById('user-license');
                    userLicenseElement.textContent = userData.License || ''; // Exibe a licença ou 'N/A' se não houver licença

                    // Verificar se o campo 'hwid' está vazio
                    if (!userData.hwid) {
                        // Se o campo 'hwid' estiver vazio, atualize-o com o novo valor
                        const updatedUserData = {
                            ...userData,
                            hwid: urlParams.hwid || '', // Use o valor do URL ou defina um valor padrão
                        };

                        // Atualizar o campo 'hwid' no banco de dados
                        set(userRef, updatedUserData).then(() => {
                            console.log('HWID atualizado com sucesso:', updatedUserData.hwid);
                            location.reload();
                        }).catch((error) => {
                            console.error('Erro ao atualizar o HWID:', error);
                        });
                    }

                    const updatedUserData = {
                        ...userData,
                        version: urlParams.version || userData.version || '',
                        License: userData.License || '',
                    };

                    // Chamar a função que depende de userData dentro deste bloco
                    updateSoftwareStatusAndVersion(updatedUserData, userRef);

                    // Adicionar lógica para mostrar ou ocultar os botões com base na existência da licença e no tempo de expiração
                    if (userData.License) {
                        const licensesRef = ref(db, `licenses/${userData.License}`);
                        get(licensesRef).then((licenseSnapshot) => {
                            const licenseData = licenseSnapshot.val();
                            if (licenseData) {
                                const expirationDate = new Date(licenseData.LicenseExpiration);
                                const remainingTotalSeconds = calculateRemainingSeconds(expirationDate);

                                if (remainingTotalSeconds < 0) {
                                    // Se o tempo de licença expirou, esconda o botão de lançamento e mostre o botão de ativar licença
                                    launchButton.style.display = 'none';
                                    activateLicenseButton.style.display = 'block';
                                } else {
                                    // Se o tempo de licença não expirou, mostre o botão de lançamento e esconda o botão de ativar licença
                                    launchButton.style.display = 'block';
                                    activateLicenseButton.style.display = 'none';
                                }
                            } else {
                                // Se a licença não puder ser encontrada, remova a licença do usuário
                                const updatedUserData = {
                                    ...userData,
                                    License: '', // Define a licença como vazia
                                };
                                set(userRef, updatedUserData).then(() => {
                                    console.log('Licença removida do usuário:', updatedUserData);
                                    location.reload();
                                }).catch((error) => {
                                    console.error('Erro ao remover a licença do usuário:', error);
                                });
                            }
                        }).catch((error) => {
                            console.error('Error fetching license data:', error);
                        });
                    } else {
                        // Se o usuário não tem uma licença, apenas ajuste a visibilidade dos botões
                        launchButton.style.display = 'none';
                        activateLicenseButton.style.display = 'block';
                    }
                } else {
                    // Se o usuário não existe, crie um novo registro para o usuário
                    const newUserData = {
                        email: user.email,
                        status: 'Active',
                        hwid: urlParams.hwid || '',
                        License: '', // Pode definir um valor padrão se necessário
                    };

                    // Adiciona os dados do usuário no banco de dados
                    set(userRef, newUserData).then(() => {
                        console.log('Novo usuário cadastrado com sucesso no banco de dados:', newUserData);
                        location.reload();

                        // Restante do código para exibir elementos, atualizar status, etc.
                        userEmailElement.textContent = newUserData.email;
                        // ... (restante do seu código)
                    }).catch((error) => {
                        console.error('Erro ao cadastrar novo usuário no banco de dados:', error);
                    });
                }
            });
        } else {
            window.location.href = 'login.html';
        }
    });
});













function updateSoftwareStatusAndVersion(userData, userRef) {
    if (!userData) {
        console.error('User data is undefined.');
        return;
    }

    const urlParams = getUrlParams();
    const currentHwid = urlParams.hwid;
    const userVersionElement = document.getElementById('user-version'); 

    console.log('HWID do usuário atual:', currentHwid);

    const softwareRef = ref(db, 'software');

    // Adicione essas variáveis no escopo global
    const softwareStatusElement = document.getElementById('software-status');
    const softwareVersionElement = document.getElementById('software-version');
    const softwareStatusIconElement = softwareStatusElement.nextElementSibling.querySelector('i');
    const loaderVersionElement = document.getElementById('loader-version');
    const hwidStatusElement = document.getElementById('hwid-status');
    const userEmailElement = document.getElementById('user-email');
    const loadingElement = document.getElementById('loading');
    const launchButton = document.getElementById('launch-button');


    get(softwareRef).then((snapshot) => {
        if (snapshot.exists()) {
            const softwareData = snapshot.val();

            const accountStatusElement = document.getElementById('account-status');
            const accountStatusContainer = document.getElementById('account-status-container');
            const statusIconElement = accountStatusContainer.querySelector('i');

            accountStatusElement.textContent = userData.status;

            if (statusIconElement) {
                statusIconElement.classList.remove('fas', 'fa-check-circle', 'fa-exclamation-circle', 'fa-times-circle', 'green', 'yellow', 'red');
            }

            if (userData.status === 'Active') {
                accountStatusElement.style.color = '#4caf50';
                if (statusIconElement) {
                    statusIconElement.classList.add('fas', 'fa-check-circle', 'green');
                }
            } else if (userData.status === 'Out-Of-Date') {
                accountStatusElement.style.color = '#ffeb3b';
                if (statusIconElement) {
                    statusIconElement.classList.add('fas', 'fa-exclamation-circle', 'yellow');
                }
            } else if (userData.status === 'Disabled') {
                accountStatusElement.style.color = '#ff0000';
                if (statusIconElement) {
                    statusIconElement.classList.add('fas', 'fa-times-circle', 'red');
                }
            }

            if (softwareStatusIconElement) {
                softwareStatusIconElement.classList.remove('fas', 'fa-check-circle', 'fa-exclamation-circle', 'fa-times-circle', 'green', 'yellow', 'red');
            }

            if (softwareData.status === 'Updated') {
                softwareStatusElement.style.color = '#4caf50';
                softwareStatusElement.textContent += 'Updated ';
                softwareStatusElement.innerHTML += '<i class="fas fa-check-circle green"></i>';
            } else {
                softwareStatusElement.style.color = '#ffeb3b';
                softwareStatusElement.textContent += 'Outdated ';
                softwareStatusElement.innerHTML += '<i class="fas fa-exclamation-circle yellow"></i>';
            }

            

            softwareVersionElement.textContent = `Lastest Version: ${softwareData.version}`;
            userVersionElement.textContent = `Your Version: ${userData.version || 'N/A'}`;
            const loaderVersion = urlParams.version;

            loaderVersionElement.textContent = '';

            if (loaderVersion && loaderVersion === softwareData.version) {
                loaderVersionElement.style.color = '#4caf50';
                loaderVersionElement.textContent += 'Updated ';
                loaderVersionElement.innerHTML += '<i class="fas fa-check-circle green"></i>';
            } else {
                loaderVersionElement.style.color = '#ffeb3b';
                loaderVersionElement.textContent += 'Outdated ';
                loaderVersionElement.innerHTML += '<i class="fas fa-exclamation-circle yellow"></i>';
            }

            if (currentHwid && currentHwid === userData.hwid) {
                hwidStatusElement.textContent = 'OK ';
                hwidStatusElement.style.color = '#4caf50';
                hwidStatusElement.nextElementSibling.innerHTML = '<i class="fas fa-check-circle green"></i>';
            } else {
                hwidStatusElement.style.color = '#ffeb3b';
                hwidStatusElement.textContent += 'Mismatched ';
                hwidStatusElement.innerHTML += '<i class="fas fa-exclamation-circle yellow"></i>';
            }

            console.log('HWID do usuário atual:', userData.hwid);

            

            get(userRef).then((userSnapshot) => {
                if (!userSnapshot.exists()) {
                    const newUser = {
                        email: user.email,
                        status: 'Active',
                        hwid: currentHwid,
                    };

                    launchButton.style.display = 'block';


                }

            // Adicione estas linhas para exibir a versão do usuário
// Adicione estas linhas para exibir a versão do usuário
const userLicense = userData.License;
const expirationDateElement = document.getElementById('expiration-date');

if (userLicense) {
    const licensesRef = ref(db, `licenses/${userLicense}`);
    get(licensesRef).then((licenseSnapshot) => {
        const licenseData = licenseSnapshot.val();

        if (licenseData) {
            const licenseExpirationDate = (licenseData.LicenseExpiration);
            const remainingTimeFormatted = calculateTimeRemaining(licenseExpirationDate);
            const remainingTotalSeconds = calculateRemainingSeconds(licenseExpirationDate);

            // Adicione estas linhas para obter a diferença entre o tempo restante e zero
            const isExpired = remainingTotalSeconds <= 0;

            // Adicione essas linhas para obter o elemento do HTML onde o tempo restante é exibido
            const expirationDateElement = document.getElementById('expiration-date');

            // Adicione essas linhas para definir o conteúdo e a cor do texto com base no status
            expirationDateElement.textContent = isExpired ? 'Expired' : remainingTimeFormatted;
            expirationDateElement.style.color = isExpired ? 'red' : '#4CAF50';

            updateGlobalStatus(userData, softwareData, urlParams, currentHwid, remainingTotalSeconds);
        } else {
            console.error('License data not found for the user.');
        }
    }).catch((error) => {
        console.error('Error fetching license data:', error);
    });
} else {
    console.error('User does not have a license.');
}


            });
        }
    });
}




function calculateTimeRemaining(expirationDate) {
    console.log('Conteúdo de expirationDate:', expirationDate);
    if (expirationDate === 'Lifetime') {
        return 'Lifetime';
    }

    const expirationDateTimeUTC = new Date(expirationDate + ' UTC');
    const currentDateUTC = new Date();
    const timeDifferenceUTC = expirationDateTimeUTC - currentDateUTC;

    if (timeDifferenceUTC <= 0) {
        return 'Expired';
    }

    const remainingMonths = Math.floor(timeDifferenceUTC / (30 * 24 * 60 * 60 * 1000));
    const remainingDays = Math.floor((timeDifferenceUTC % (30 * 24 * 60 * 60 * 1000)) / (24 * 60 * 60 * 1000));
    const remainingHours = Math.floor((timeDifferenceUTC % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
    const remainingMinutes = Math.floor((timeDifferenceUTC % (60 * 60 * 1000)) / (60 * 1000));
    const remainingSeconds = Math.floor((timeDifferenceUTC % (60 * 1000)) / 1000);

    let remainingTime = '';

    if (remainingMonths > 0) {
        remainingTime += `${remainingMonths}mo `;
    }
    if (remainingDays > 0) {
        remainingTime += `${remainingDays}d `;
    }
    if (remainingHours > 0) {
        remainingTime += `${remainingHours}h `;
    }
    if (remainingMinutes > 0) {
        remainingTime += `${remainingMinutes}min `;
    }
    if (remainingSeconds > 0) {
        remainingTime += `${remainingSeconds}s `;
    }

    return remainingTime.trim();
}







function calculateRemainingSeconds(expirationDate) {
    if (expirationDate === 'Lifetime') {
        return 9999999999;
    }

    const expirationDateTimeUTC = new Date(expirationDate + ' UTC');
    const currentDateUTC = new Date();
    const timeDifferenceUTC = expirationDateTimeUTC.getTime() - currentDateUTC.getTime();

    if (timeDifferenceUTC <= 0) {
        return 'Expired';
    }

    // Convertendo a diferença de milissegundos para segundos
    const remainingTotalSeconds = Math.floor(timeDifferenceUTC / 1000);

    console.log("ID02::::::", remainingTotalSeconds);
    return remainingTotalSeconds;
}












// Adicione ao seu script panel-javascript.js
const activateLicenseButton = document.getElementById('activate-license-button');
const licensePopup = document.getElementById('license-popup');
const submitLicenseButton = document.getElementById('submit-license');
const licenseInput = document.getElementById('license-input');

activateLicenseButton.addEventListener('click', () => {
    licensePopup.style.display = 'flex';
});







// Função para formatar a data no formato "YYYY-MM-DD HH:mm:ss"
function formatDateTime(date) {
    const year = date.getUTCFullYear();
    const month = (date.getUTCMonth() + 1).toString().padStart(2, '0'); // Mês é baseado em zero
    const day = date.getUTCDate().toString().padStart(2, '0');
    const hours = date.getUTCHours().toString().padStart(2, '0');
    const minutes = date.getUTCMinutes().toString().padStart(2, '0');
    const seconds = date.getUTCSeconds().toString().padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}


// Função para calcular e definir a data de expiração da licença
function calculateLicenseExpiration(licenseDuration) {
    if (licenseDuration.toLowerCase() === 'lifetime') {
        // Se a licença for vitalícia, a data de expiração é "Lifetime"
        return 'Lifetime';
    }

    // Se não for uma licença vitalícia, calcula a data de expiração com base na duração
    const currentDate = new Date();
    const durationParts = licenseDuration.split(' ');
    const durationValue = parseInt(durationParts[0]);
    const durationUnit = durationParts[1].toLowerCase();

    let expirationDate;

    if (durationUnit === 'hours') {
        expirationDate = new Date(currentDate.getTime() + durationValue * 60 * 60 * 1000);
    } else if (durationUnit === 'days') {
        expirationDate = new Date(currentDate.getTime() + durationValue * 24 * 60 * 60 * 1000);
    } else if (durationUnit === 'months') {
        expirationDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + durationValue, currentDate.getDate());
    }

    return expirationDate ? formatDateTime(expirationDate) : '';
}


// ...



// ...

submitLicenseButton.addEventListener('click', () => {
    const licenseValue = licenseInput.value.trim();

    if (licenseValue) {
        const licensesRef = ref(db, `licenses/${licenseValue}`);

        get(licensesRef).then((licenseSnapshot) => {
            const licenseData = licenseSnapshot.val();

            if (licenseData && !licenseData.licenseActivated) {
                // A licença existe e ainda não foi ativada
                console.log('License found:', licenseData);

                onAuthStateChanged(auth, (user) => {
                    if (user) {
                        const userRef = ref(db, `users/${user.uid}`);
                        get(userRef).then((userSnapshot) => {
                            if (userSnapshot.exists()) {
                                const userData = userSnapshot.val();

                                // Obter HWID da URL
                                const urlParams = new URLSearchParams(window.location.search);
                                const hwidFromUrl = urlParams.get('hwid') || '';

                                const updatedUserData = {
                                    ...userData,
                                    License: licenseValue,
                                    hwid: hwidFromUrl // Atualiza com novo HWID
                                };

                                const expirationDate = calculateLicenseExpiration(licenseData.LicenseDuration);
                                const extraInfo = `User Email: ${user.email}`;

                                set(userRef, updatedUserData).then(() => {
                                    console.log('User updated:', updatedUserData);

                                    const updatedLicenseData = {
                                        ...licenseData,
                                        licenseActivated: true,
                                        LicenseExpiration: expirationDate,
                                        ExtraInfo: extraInfo,
                                    };

                                    set(licensesRef, updatedLicenseData).then(() => {
                                        console.log('License activated:', licenseValue);
                                        location.reload();
                                    }).catch((error) => {
                                        console.error('Error updating license data:', error);
                                    });

                                    showNotification('License activated successfully!', 'alert-success', 'fas fa-check-circle');
                                }).catch((error) => {
                                    console.error('Error updating user data:', error);
                                    showNotification('Failed to activate license. Please try again.', 'alert-warning', 'fas fa-exclamation-circle');
                                });
                            } else {
                                console.error('User data not found in the database.');
                                showNotification('Failed to activate license. Please try again.', 'alert-warning', 'fas fa-exclamation-circle');
                            }
                        }).catch((error) => {
                            console.error('Error fetching user data:', error);
                            showNotification('Failed to activate license. Please try again.', 'alert-warning', 'fas fa-exclamation-circle');
                        });
                    } else {
                        console.error('User not authenticated.');
                        showNotification('User not authenticated. Please log in and try again.', 'alert-warning', 'fas fa-exclamation-circle');
                    }
                });
            } else if (licenseData && licenseData.licenseActivated) {
                console.log('License already activated:', licenseValue);
                showNotification('License already activated. Please enter a valid license.', 'alert-warning', 'fas fa-exclamation-circle');
            } else {
                console.log('License not found:', licenseValue);
                showNotification('Invalid license. Please enter a valid license.', 'alert-warning', 'fas fa-exclamation-circle');
            }
        }).catch((error) => {
            console.error('Error fetching license data:', error);
            showNotification('Failed to activate license. Please try again.', 'alert-warning', 'fas fa-exclamation-circle');
        });
    } else {
        showNotification('Please enter a valid license.', 'alert-warning', 'fas fa-exclamation-circle');
    }
});

// ...










// Adicione um evento de clique ao botão de fechar o popup
const popupClose = document.getElementById('popup-close');
popupClose.addEventListener('click', () => {
    licensePopup.style.display = 'none';
});


