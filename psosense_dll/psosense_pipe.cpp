#include <Windows.h>
#include <iostream>
#include <thread>
#include <atomic>
#include <string>
#include <unordered_map>
#include <functional>

#include "psosense_pipe.hpp"
#include "function_calls.hpp"
#include "dx11_hook.hpp"

static HANDLE hPipe = INVALID_HANDLE_VALUE;
static std::thread pipeThread;
static std::atomic_bool running = false;

// Mapeamento de comandos para funções
static std::unordered_map<std::string, std::function<void()>> commandMap = {
    {"force_swap", ExecuteInitiateSwap},
    {"spawn_ball", ExecuteSpawnBall},
    {"reset_match", ExecuteForceResetMatch},
    {"toggle_keeper", ExecuteToggleSingleKeeper},
    {"enable_antikick", ExecuteEnableAntiKick},
    {"disable_antikick", ExecuteDisableAntiKick},
    {"enable_touchslow", ExecuteEnableTouchSlow},
    {"disable_touchslow", ExecuteDisableTouchSlow},
    {"enable_watermark", EnableWatermark},
    {"disable_watermark", DisableWatermark},
};


// Manipulador de comandos recebidos
void HandleCommand(const std::string& cmd)
{
    auto it = commandMap.find(cmd);
    if (it != commandMap.end())
    {
        it->second(); // Executa a função mapeada
    }
    else
    {
        std::cout << "[CMD] Comando desconhecido: " << cmd << "\n";
    }
}
void PipeListener()
{
    while (running)
    {
        hPipe = CreateNamedPipeA(
            R"(\\.\pipe\psosense)",
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            PIPE_UNLIMITED_INSTANCES, 1024, 1024, 0, nullptr
        );

        if (hPipe == INVALID_HANDLE_VALUE)
        {
            std::cerr << "[ERRO] Falha ao criar o pipe.\n";
            Sleep(1000);
            continue;
        }

        std::cout << "[OK] Pipe criado. Aguardando conexão...\n";

        if (!ConnectNamedPipe(hPipe, nullptr) && GetLastError() != ERROR_PIPE_CONNECTED)
        {
            std::cerr << "[ERRO] Falha ao conectar cliente ao pipe.\n";
            CloseHandle(hPipe);
            hPipe = INVALID_HANDLE_VALUE;
            continue;
        }

        std::cout << "[OK] Cliente conectado ao pipe.\n";

        char buffer[1024];
        DWORD bytesRead;

        while (running && hPipe != INVALID_HANDLE_VALUE)
        {
            ZeroMemory(buffer, sizeof(buffer));

            BOOL result = ReadFile(hPipe, buffer, sizeof(buffer) - 1, &bytesRead, nullptr);
            if (!result || bytesRead == 0)
            {
                std::cout << "[INFO] Cliente desconectado.\n";
                break;
            }

            buffer[bytesRead] = '\0';
            std::string cmd(buffer);

            std::cout << "[PIPE] Mensagem recebida: " << cmd << "\n";
            HandleCommand(cmd);

            const char* resposta = "Recebido com sucesso!";
            DWORD bytesWritten;
            WriteFile(hPipe, resposta, strlen(resposta), &bytesWritten, nullptr);
        }

        if (hPipe != INVALID_HANDLE_VALUE)
        {
            DisconnectNamedPipe(hPipe);
            CloseHandle(hPipe);
            hPipe = INVALID_HANDLE_VALUE;
        }
    }
}


void StartPipeServer()
{
    if (running) return;

    running = true;
    pipeThread = std::thread(PipeListener);
    pipeThread.detach();
}

void StopPipeServer()
{
    running = false;
    if (hPipe != INVALID_HANDLE_VALUE)
    {
        CloseHandle(hPipe);
        hPipe = INVALID_HANDLE_VALUE;
    }
}
