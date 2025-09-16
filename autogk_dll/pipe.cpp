#define WIN32_LEAN_AND_MEAN          // Evita inclusão desnecessária de headers antigos como <winsock.h>

#include <winsock2.h>                // Sempre deve vir antes de <windows.h>
#include <ws2tcpip.h>                // Necessário para getaddrinfo e inet_ntop
#include <windows.h>                 // Só depois de winsock2.h

#include <string>
#include <iostream>
#include <wininet.h>
#include <sstream>
#include <thread>

#include "pipe.hpp"                  // Seu header, pode ficar depois dos headers padrão

#pragma comment(lib, "Ws2_32.lib")
#pragma comment(lib, "wininet.lib")



#define PIPE_NAME R"(\\.\pipe\autogk)"
#define VALIDATION_URL_PATH "/token"
const char* VALIDATION_HOST = "181.215.45.160";


#define VALIDATION_PORT 5000


bool VerificaTokenComServidor(const std::wstring& token)
{
    std::string tokenUtf8(token.begin(), token.end());
    std::string payload = "{\"token\":\"" + tokenUtf8 + "\"}";

    while (true)
    {
        std::cout << "[VALIDACAO] Tentando conectar ao servidor...\n";

        HINTERNET hInternet = InternetOpenA("AutoGK", INTERNET_OPEN_TYPE_DIRECT, nullptr, nullptr, 0);
        if (!hInternet)
        {
            std::cerr << "[ERRO] InternetOpenA falhou. Retentando em 2s...\n";
            std::this_thread::sleep_for(std::chrono::seconds(2));
            continue;
        }

        HINTERNET hConnect = InternetConnectA(hInternet, VALIDATION_HOST, VALIDATION_PORT, nullptr, nullptr, INTERNET_SERVICE_HTTP, 0, 0);
        if (!hConnect)
        {
            std::cerr << "[ERRO] InternetConnectA falhou. Retentando em 2s...\n";
            InternetCloseHandle(hInternet);
            std::this_thread::sleep_for(std::chrono::seconds(2));
            continue;
        }

        // Inicializa Winsock
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
        {
            std::cerr << "[SECURITY] WSAStartup falhou.\n";
            InternetCloseHandle(hConnect);
            InternetCloseHandle(hInternet);
            continue;
        }

        addrinfo hints = {};
        hints.ai_family = AF_INET;
        addrinfo* result = nullptr;

        if (getaddrinfo(VALIDATION_HOST, nullptr, &hints, &result) != 0)
        {
            std::cerr << "[SECURITY] getaddrinfo falhou.\n";
            WSACleanup();
            InternetCloseHandle(hConnect);
            InternetCloseHandle(hInternet);
            continue;
        }

        sockaddr_in* sockaddr = reinterpret_cast<sockaddr_in*>(result->ai_addr);
        char ipStr[INET_ADDRSTRLEN] = {};
        inet_ntop(AF_INET, &(sockaddr->sin_addr), ipStr, INET_ADDRSTRLEN);

        std::string resolvedIp = ipStr;
        freeaddrinfo(result);
        WSACleanup();

        if (resolvedIp != "181.215.45.160")
        {
            std::cerr << "[SECURITY] IP resolvido invalido: " << resolvedIp << " (esperado: 181.215.45.160)\n";
            InternetCloseHandle(hConnect);
            InternetCloseHandle(hInternet);
            continue;
        }

        HINTERNET hRequest = HttpOpenRequestA(hConnect, "POST", VALIDATION_URL_PATH, nullptr, nullptr, nullptr, INTERNET_FLAG_RELOAD, 0);
        if (!hRequest)
        {
            std::cerr << "[ERRO] HttpOpenRequestA falhou. Retentando em 2s...\n";
            InternetCloseHandle(hConnect);
            InternetCloseHandle(hInternet);
            std::this_thread::sleep_for(std::chrono::seconds(2));
            continue;
        }

        const char* headers = "Content-Type: application/json\r\n";
        if (!HttpSendRequestA(hRequest, headers, -1L, (LPVOID)payload.c_str(), payload.size()))
        {
            std::cerr << "[ERRO] HttpSendRequestA falhou. Retentando em 2s...\n";
            InternetCloseHandle(hRequest);
            InternetCloseHandle(hConnect);
            InternetCloseHandle(hInternet);
            std::this_thread::sleep_for(std::chrono::seconds(2));
            continue;
        }

        // Lê a resposta
        char buffer[512] = { 0 };
        DWORD bytesRead = 0;
        std::stringstream responseStream;

        while (InternetReadFile(hRequest, buffer, sizeof(buffer) - 1, &bytesRead) && bytesRead != 0)
        {
            buffer[bytesRead] = '\0';
            responseStream << buffer;
        }

        std::string response = responseStream.str();
        std::cout << "[DEBUG] Resposta do servidor: " << response << "\n";

        InternetCloseHandle(hRequest);
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hInternet);

        if (response.find("\"valid\":true") != std::string::npos ||
            response.find("\"valid\": true") != std::string::npos)
        {
            std::cout << "[VALIDACAO] Token validado com sucesso.\n";
            return true;
        }
        else if (response.find("\"valid\":false") != std::string::npos ||
            response.find("\"valid\": false") != std::string::npos)
        {
            std::cerr << "[VALIDACAO] Token recusado pelo servidor.\n";
            return false;
        }
        else
        {
            std::cerr << "[ERRO] Resposta inesperada. Retentando em 2s...\n";
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }
    }
}



bool AguardaTokenEValida()
{
    std::cout << "[PIPE] Criando named pipe em: " << PIPE_NAME << "\n";

    HANDLE hPipe = CreateNamedPipeA(
        PIPE_NAME,
        PIPE_ACCESS_DUPLEX,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
        1, 1024, 1024, 0, nullptr
    );

    if (hPipe == INVALID_HANDLE_VALUE)
    {
        std::cerr << "[ERRO] Falha ao criar o named pipe.\n";
        return false;
    }

    std::cout << "[PIPE] Aguardando conexao do cliente...\n";

    BOOL conectado = ConnectNamedPipe(hPipe, nullptr) ? TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);
    if (!conectado)
    {
        std::cerr << "[ERRO] Falha ao conectar com cliente.\n";
        CloseHandle(hPipe);
        return false;
    }

    std::cout << "[PIPE] Cliente conectado. Lendo token...\n";

    wchar_t buffer[256] = { 0 };
    DWORD bytesLidos = 0;
    BOOL lido = ReadFile(hPipe, buffer, sizeof(buffer) - sizeof(wchar_t), &bytesLidos, nullptr);

    if (!lido || bytesLidos == 0)
    {
        std::cerr << "[ERRO] Falha ao ler token do pipe.\n";
        CloseHandle(hPipe);
        return false;
    }

    buffer[bytesLidos / sizeof(wchar_t)] = L'\0';
    std::wstring token(buffer);
    std::wcout << L"[PIPE] Token recebido: " << token << L"\n";

    // Envia confirmação imediata
    const wchar_t* respostaImediata = L"ok";
    DWORD bytesEscritos;
    WriteFile(hPipe, respostaImediata, (wcslen(respostaImediata) + 1) * sizeof(wchar_t), &bytesEscritos, nullptr);
    std::cout << "[PIPE] 'ok' enviado ao cliente.\n";

    CloseHandle(hPipe);  // Encerramos o pipe: o cliente não precisa mais dele

    // Validação com o servidor
    return VerificaTokenComServidor(token);
}
