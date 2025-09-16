#include "antikick.hpp"
#include "MinHook/include/MinHook.h"
#include "SDK.hpp"
#include <iostream>
#include <Windows.h>

// Offset conhecido de ProcessEvent relativo ao ImageBase
constexpr uintptr_t ProcessEventOffset = 0x010D8E60;

// Controle interno
static bool g_AntiKickEnabled = false;

// Ponteiro original
using tProcessEvent = void(*)(SDK::UObject*, SDK::UFunction*, void*);
static tProcessEvent OriginalProcessEvent = nullptr;

// Função hookada
void HookedProcessEvent(SDK::UObject* obj, SDK::UFunction* func, void* params)
{
    if (!obj || !func)
    {
        OriginalProcessEvent(obj, func, params);
        return;
    }

    const std::string functionName = func->GetName();

    if (functionName == "RecieveKick")
    {
        std::cout << "[HOOK] RecieveKick interceptado.\n";

        if (g_AntiKickEnabled)
        {
            std::cout << "[ANTIKICK] Kick bloqueado pelo cliente.\n";
            return; // Bloqueia o kick
        }
        else
        {
            std::cout << "[ANTIKICK] Kick permitido.\n";
        }
    }

    OriginalProcessEvent(obj, func, params);
}

// Inicializa o hook em ProcessEvent
void InitializeAntiKick()
{
    const uintptr_t imageBase = SDK::InSDKUtils::GetImageBase();
    const uintptr_t realAddress = imageBase + ProcessEventOffset;

    if (MH_Initialize() != MH_OK && MH_Initialize() != MH_ERROR_ALREADY_INITIALIZED)
    {
        std::cerr << "[ANTIKICK] Falha ao inicializar MinHook.\n";
        return;
    }

    if (MH_CreateHook(
        reinterpret_cast<LPVOID>(realAddress),
        &HookedProcessEvent,
        reinterpret_cast<void**>(&OriginalProcessEvent)) != MH_OK)
    {
        std::cerr << "[ANTIKICK] Falha ao criar hook em ProcessEvent.\n";
        return;
    }

    if (MH_EnableHook(reinterpret_cast<LPVOID>(realAddress)) != MH_OK)
    {
        std::cerr << "[ANTIKICK] Falha ao ativar hook.\n";
        return;
    }

    std::cout << "[ANTIKICK] Hook em ProcessEvent instalado com sucesso.\n";
}

// Ativa ou desativa a proteção contra kick
void SetAntiKickEnabled(bool enabled)
{
    g_AntiKickEnabled = enabled;
    std::cout << "[ANTIKICK] Proteção " << (enabled ? "ATIVADA" : "DESATIVADA") << ".\n";
}

// Consulta o estado atual
bool IsAntiKickEnabled()
{
    return g_AntiKickEnabled;
}
