#include "MinHook/include/MinHook.h"
#include "SDK.hpp"
#include <Windows.h>
#include <iostream>
#include <regex>
#include <string>

// === CONFIGURAÇÕES ===
constexpr uintptr_t ProcessEventOffset = 0x010D8E60;
using tProcessEvent = void(*)(SDK::UObject*, SDK::UFunction*, void*);
static tProcessEvent OriginalProcessEvent = nullptr;

// === Remove apenas o campo "BanReason" do JSON ===
std::string SanitizeJson(const std::string& json)
{
    std::regex banPattern(R"(,\s*\"BanReason\"\s*:\s*\".+?\")");
    return std::regex_replace(json, banPattern, "");
}

// === Hook da função ProcessEvent ===
void HookedProcessEvent(SDK::UObject* obj, SDK::UFunction* func, void* params)
{
    if (!obj || !func) {
        OriginalProcessEvent(obj, func, params);
        return;
    }

    const std::string name = func->GetName();

    // Protege contra kick
    if (name == "RecieveKick")
    {
        std::cout << "[PSOSENSE] RecieveKick blocked.\n";
        return;
    }

    // Remove campo BanReason do JSON de resposta
    if (name == "UpdateSteamNameSuccess")
    {
        struct {
            SDK::UVaRestRequestJSON* Request;
        }*typedParams = reinterpret_cast<decltype(typedParams)>(params);

        if (typedParams && typedParams->Request)
        {
            SDK::FString rawFStr = typedParams->Request->GetResponseContentAsString(true);
            std::string originalJson = rawFStr.ToString();

            if (!originalJson.empty())
            {
                std::string sanitized = SanitizeJson(originalJson);
                std::wstring wide(sanitized.begin(), sanitized.end());
                typedParams->Request->ResponseContent = SDK::FString(wide.c_str());

                std::cout << "[PSOSENSE] BanReason field removed.\n";
            }
        }
    }

    // Chama a função original
    OriginalProcessEvent(obj, func, params);
}

// === Inicialização pública ===
void InitializeSpoofer()
{
    static bool initialized = false;
    if (initialized) return;

    const uintptr_t base = SDK::InSDKUtils::GetImageBase();
    const uintptr_t addr = base + ProcessEventOffset;

    if (MH_Initialize() != MH_OK && MH_Initialize() != MH_ERROR_ALREADY_INITIALIZED)
    {
        std::cerr << "[PSOSENSE] Failed to initialize MinHook.\n";
        return;
    }

    if (MH_CreateHook(reinterpret_cast<void*>(addr), &HookedProcessEvent,
        reinterpret_cast<void**>(&OriginalProcessEvent)) != MH_OK)
    {
        std::cerr << "[PSOSENSE] Failed to create hook on ProcessEvent.\n";
        return;
    }

    if (MH_EnableHook(reinterpret_cast<void*>(addr)) != MH_OK)
    {
        std::cerr << "[PSOSENSE] Failed to enable ProcessEvent hook.\n";
        return;
    }

    initialized = true;
    std::cout << "[PSOSENSE] Spoofer active. Kick protection + BanReason removal enabled.\n";
}
