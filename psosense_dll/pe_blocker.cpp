#include "pe_blocker.hpp"
#include "MinHook/include/MinHook.h"
#include "SDK.hpp"
#include <iostream>
#include <Windows.h>
#include <unordered_map>
#include <string>

// Offset conhecido de ProcessEvent relativo ao ImageBase
constexpr uintptr_t ProcessEventOffset = 0x010D8E60;

// Ponteiro original
using tProcessEvent = void(*)(SDK::UObject*, SDK::UFunction*, void*);
static tProcessEvent OriginalProcessEvent = nullptr;

// Controle de funções bloqueadas
static std::unordered_map<std::string, bool> blockedFunctions = {
    {"RecieveKick", false},
    {"StartTouchSlowDown", false},
};

// Hook da ProcessEvent
void HookedProcessEvent(SDK::UObject* obj, SDK::UFunction* func, void* params)
{
    if (!obj || !func)
    {
        OriginalProcessEvent(obj, func, params);
        return;
    }

    const std::string functionName = func->GetName();

    auto it = blockedFunctions.find(functionName);
    if (it != blockedFunctions.end() && it->second)
    {
        std::cout << "[HOOK] Função bloqueada: " << functionName << "\n";
        return; // Bloqueia a função
    }

    OriginalProcessEvent(obj, func, params);
}

// Inicializa o hook
void InitializeFunctionBlocker()
{
    const uintptr_t imageBase = SDK::InSDKUtils::GetImageBase();
    const uintptr_t realAddress = imageBase + ProcessEventOffset;

    if (MH_Initialize() != MH_OK && MH_Initialize() != MH_ERROR_ALREADY_INITIALIZED)
    {
        std::cerr << "[HOOK] Falha ao inicializar MinHook.\n";
        return;
    }

    if (MH_CreateHook(
        reinterpret_cast<LPVOID>(realAddress),
        &HookedProcessEvent,
        reinterpret_cast<void**>(&OriginalProcessEvent)) != MH_OK)
    {
        std::cerr << "[HOOK] Falha ao criar hook em ProcessEvent.\n";
        return;
    }

    if (MH_EnableHook(reinterpret_cast<LPVOID>(realAddress)) != MH_OK)
    {
        std::cerr << "[HOOK] Falha ao ativar hook.\n";
        return;
    }

    std::cout << "[HOOK] Hook em ProcessEvent instalado com sucesso.\n";
}

// Gerenciamento geral de bloqueios
void SetFunctionBlocked(const std::string& functionName, bool enabled)
{
    if (blockedFunctions.find(functionName) != blockedFunctions.end())
    {
        blockedFunctions[functionName] = enabled;
        std::cout << "[HOOK] Bloqueio de '" << functionName << "' " << (enabled ? "ATIVADO" : "DESATIVADO") << ".\n";
    }
    else
    {
        std::cerr << "[HOOK] Função desconhecida: " << functionName << ".\n";
    }
}

bool IsFunctionBlocked(const std::string& functionName)
{
    auto it = blockedFunctions.find(functionName);
    return it != blockedFunctions.end() && it->second;
}

// Wrappers específicos
void SetAntiKickEnabled(bool enabled)
{
    SetFunctionBlocked("RecieveKick", enabled);
}

bool IsAntiKickEnabled()
{
    return IsFunctionBlocked("RecieveKick");
}

void SetTouchSlowEnabled(bool enabled)
{
    SetFunctionBlocked("StartTouchSlowDown", enabled);
}

bool IsTouchSlowEnabled()
{
    return IsFunctionBlocked("StartTouchSlowDown");
}
