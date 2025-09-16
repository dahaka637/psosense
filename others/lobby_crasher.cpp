#include "game_context.hpp"
#include "SDK.hpp"
#include <thread>
#include <atomic>
#include <chrono>
#include <mutex>

// Variáveis de controle global (externas)
extern bool g_LobbyCrasherActive;
extern int g_CrashIntervalMs;

// Internas
static std::thread g_LobbyCrasherThread;
static std::mutex g_Locker;
static std::atomic<bool> g_IsRunning{ false };

// Valida e recupera ponteiros de função
static bool GetValidFunctions(SDK::UFunction*& startFunc, SDK::UFunction*& resetFunc)
{
    if (!InitializeGameContext())
        return false;

    const auto* controller = gContext.SPController;
    if (!controller || !controller->Class || !gContext.CustomGameState)
        return false;

    startFunc = controller->Class->GetFunction("SP_Controller_C", "CL_Host_ForceStartMatch");
    resetFunc = controller->Class->GetFunction("SP_Controller_C", "CL_Host_ForceResetMatch");

    return startFunc && resetFunc &&
        reinterpret_cast<uintptr_t>(startFunc) > 0x10000 &&
        reinterpret_cast<uintptr_t>(resetFunc) > 0x10000;
}

// Loop principal do Crasher
static void LobbyCrasherLoop()
{
    while (g_LobbyCrasherActive)
    {
        SDK::UFunction* startFunc = nullptr;
        SDK::UFunction* resetFunc = nullptr;

        if (!GetValidFunctions(startFunc, resetFunc))
        {
            g_LobbyCrasherActive = false;
            break;
        }

        if (gContext.SPController && startFunc)
            gContext.SPController->ProcessEvent(startFunc, nullptr);

        std::this_thread::sleep_for(std::chrono::milliseconds(g_CrashIntervalMs));

        if (!g_LobbyCrasherActive)
            break;

        if (gContext.SPController && resetFunc)
            gContext.SPController->ProcessEvent(resetFunc, nullptr);

        std::this_thread::sleep_for(std::chrono::milliseconds(g_CrashIntervalMs));
    }

    g_IsRunning = false;
}

// Interface pública para iniciar/parar o crasher
void ToggleLobbyCrasher()
{
    std::scoped_lock lock(g_Locker);

    if (g_LobbyCrasherActive)
    {
        g_LobbyCrasherActive = false;
        return;
    }

    if (g_IsRunning)
        return;

    g_LobbyCrasherActive = true;
    g_IsRunning = true;

    g_LobbyCrasherThread = std::thread(LobbyCrasherLoop);
    g_LobbyCrasherThread.detach();
}
