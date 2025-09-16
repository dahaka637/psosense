#include <Windows.h>
#include <thread>
#include "game_pointers.hpp"
#include "auto_gk.hpp"
#include "dx11_hook.hpp"
#include "pipe.hpp"  // Declaração da função AguardaTokenEValida

DWORD WINAPI MainThread(LPVOID)
{
    // Aguarda o token do launcher via pipe
    if (!AguardaTokenEValida())
        return 0;  // Finaliza silenciosamente se token for inválido

    // Inicializa ponteiros do jogo
    InitializeGamePointers();

    // Inicia sistema AutoGK
    AutoGK::Start();

    // Hook gráfico (ImGui + DirectX)
    HookPresent();

    // Mantém a DLL viva
    while (true)
        std::this_thread::sleep_for(std::chrono::seconds(1));

    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        DisableThreadLibraryCalls(hModule);  // Evita chamadas extras
        CreateThread(nullptr, 0, MainThread, nullptr, 0, nullptr);
    }
    return TRUE;
}
