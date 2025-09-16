#include <Windows.h>
#include "psosense_pipe.hpp"
#include "pe_blocker.hpp"
#include "dx11_hook.hpp"

#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "dwrite.lib")
#pragma comment(lib, "dxgi.lib")
#pragma comment(lib, "user32.lib")

#include "imgui.h"
#include "backends/imgui_impl_dx11.h"
#include "backends/imgui_impl_win32.h"
#include "MinHook/include/MinHook.h"

DWORD WINAPI MainThread(LPVOID)
{
    // Início silencioso — sem console, sem log

    StartPipeServer();
    InitializeFunctionBlocker();
    HookPresent();

    while (true)
    {
        if (GetAsyncKeyState(VK_END) & 1)
        {
            // Finaliza ImGui se foi inicializado
            if (imgui_initialized)
            {
                ImGui_ImplDX11_Shutdown();
                ImGui_ImplWin32_Shutdown();
                ImGui::DestroyContext();
            }

            StopPipeServer();

            // Desabilita os hooks e limpa o MinHook
            MH_DisableHook(MH_ALL_HOOKS);
            MH_Uninitialize();

            break;
        }

        Sleep(100);
    }

    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        DisableThreadLibraryCalls(hModule);
        CreateThread(nullptr, 0, MainThread, nullptr, 0, nullptr);
    }

    return TRUE;
}
