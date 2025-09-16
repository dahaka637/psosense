// index-javascript.js

// Função para redirecionar para a loja
function redirectToStore() {
    window.open("https://psosense.sellpass.io/products/Psosense-Premium", "_blank");
}

// Função para redirecionar para o servidor do Discord
function redirectToDiscord() {
    window.open("https://discord.gg/DPg7k5zZs4", "_blank");
}

// Adiciona event listener para o botão da loja
document.getElementById("store-button").addEventListener("click", redirectToStore);

// Adiciona event listener para o botão do servidor do Discord
document.getElementById("discord-button").addEventListener("click", redirectToDiscord);


document.addEventListener('DOMContentLoaded', function() {
    // Definindo o valor inicial do contador
    let count = 0;
    // Selecionando o elemento do contador
    const customerNumber = document.getElementById('customer-number');
    const clientInfo = document.querySelector('.client-info');

    // Obtendo a data atual
    const currentDate = new Date();
    // Obtendo o ano atual
    const currentYear = currentDate.getFullYear();
    // Obtendo a data de início do ano atual
    const startDate = new Date(currentYear, 0, 0);
    // Calculando a quantidade de dias passados no ano
    const elapsedDays = Math.floor((currentDate - startDate) / (1000 * 60 * 60 * 24));
    // Definindo o valor alvo baseado na quantidade de dias passados
    const targetValue = 200 + elapsedDays;

    // Função para atualizar o contador com base no progresso
    function updateCounter() {
        // Definindo o intervalo de tempo com base no progresso
        let interval;
        if (count < 150) {
            interval = 3; // Intervalo mais rápido no início
        } else if (count < 180) {
            interval = 5; // Intervalo médio na fase intermediária
        } else {
            interval = 60; // Intervalo lento no final
        }

        // Incrementando o contador
        count++;
        // Atualizando o texto do contador
        customerNumber.textContent = '+ ' + count + ' Customers!';

        // Verificando se o contador ainda não atingiu o valor alvo
        if (count < targetValue) {
            // Aplicando a classe de animação enquanto o contador estiver abaixo do valor alvo
            clientInfo.classList.add('animate');
            // Continuando a atualização do contador com o novo intervalo
            setTimeout(updateCounter, interval); // Intervalo de tempo em milissegundos
        } else {
            // Removendo a classe de animação após atingir o valor alvo
            clientInfo.classList.remove('animate');
        }
    }

    // Iniciando a atualização do contador
    updateCounter(); 
});
