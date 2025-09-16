#include "game_context.hpp"
#include <Windows.h>
#include "SDK.hpp"

GameContext gContext = {};

SDK::UWorld* GetRobustWorld()
{
    if (SDK::Offsets::GWorld != 0)
    {
        auto base = SDK::InSDKUtils::GetImageBase();
        auto worldPtr = reinterpret_cast<SDK::UWorld**>(base + SDK::Offsets::GWorld);
        if (worldPtr && *worldPtr) return *worldPtr;
    }

    auto engine = SDK::UEngine::GetEngine();
    if (engine && engine->GameViewport && engine->GameViewport->World)
        return engine->GameViewport->World;

    return nullptr;
}

bool InitializeGameContext()
{
    ZeroMemory(&gContext, sizeof(gContext));

    gContext.World = GetRobustWorld();
    if (!gContext.World) return false;

    gContext.GameInstance = gContext.World->OwningGameInstance;
    if (!gContext.GameInstance) return false;

    const auto& players = gContext.GameInstance->LocalPlayers;
    if (players.Num() == 0 || !players[0]) return false;

    gContext.LocalPlayer = players[0];
    gContext.Controller = gContext.LocalPlayer->PlayerController;
    if (!gContext.Controller) return false;

    gContext.SPController = static_cast<SDK::ASP_Controller_C*>(gContext.Controller);
    if (!gContext.SPController) return false;

    auto baseState = gContext.World->GameState;
    if (baseState && baseState->IsA(SDK::AMP_GameState_C::StaticClass()))
        gContext.CustomGameState = static_cast<SDK::AMP_GameState_C*>(baseState);

    return true;
}
