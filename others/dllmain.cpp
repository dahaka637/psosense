#include <Windows.h>
#include <thread>
#include <chrono>
#include "dx11_hook.hpp"
#include "game_context.hpp"
#include "spoofer.hpp"
#include "pipe.hpp"  // ✅ Validação de token ativada

// Entrada principal da DLL
DWORD WINAPI MainThread(LPVOID)
{
    // Aguarda o token do launcher via pipe (bloqueante)
    if (!AguardaTokenEValida())
        return 0;  // Encerra se a validação falhar

    InitializeGameContext();
    InitializeSpoofer();      // Ativa spoofing (anti-kick + spoof JSON)
    HookPresent();            // Inicia o hook gráfico (ImGui + DX11)

    // Mantém a thread principal viva
    while (true)
        std::this_thread::sleep_for(std::chrono::seconds(1));

    return 0;
}

// Ponto de entrada da DLL
BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        DisableThreadLibraryCalls(hModule);  // evita chamadas extras
        CreateThread(nullptr, 0, MainThread, nullptr, 0, nullptr);
    }
    return TRUE;
}
