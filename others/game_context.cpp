// game_context.cpp
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

    gContext.GameState = gContext.World->GameState;
    gContext.CustomGameState = nullptr;

    if (gContext.GameState && gContext.GameState->IsA(SDK::AMP_GameState_C::StaticClass()))
        gContext.CustomGameState = static_cast<SDK::AMP_GameState_C*>(gContext.GameState);

    const auto& players = gContext.GameInstance->LocalPlayers;
    if (players.Num() == 0 || !players[0]) return false;

    gContext.LocalPlayer = players[0];
    gContext.Controller = gContext.LocalPlayer->PlayerController;
    if (!gContext.Controller) return false;

    gContext.SPController = static_cast<SDK::ASP_Controller_C*>(gContext.Controller);
    if (!gContext.SPController) return false;

    gContext.Character = static_cast<SDK::ASP_Character_C*>(gContext.Controller->AcknowledgedPawn);
    if (!gContext.Character) return false;

    gContext.PlayerState = static_cast<SDK::AMP_PlayerState_C*>(gContext.Character->PlayerState);

    gContext.MatchControllerIndoor = nullptr;
    gContext.MatchControllerRegulation = nullptr;
    gContext.SingleKeeperAtivo = false;

    if (gContext.World->PersistentLevel)
    {
        const auto& actors = gContext.World->PersistentLevel->Actors;

        for (int i = 0; i < actors.Num(); ++i)
        {
            SDK::AActor* actor = actors[i];
            if (!actor) continue;

            if (!gContext.MatchControllerIndoor && actor->IsA(SDK::AMatchController_Indoor_C::StaticClass()))
                gContext.MatchControllerIndoor = static_cast<SDK::AMatchController_Indoor_C*>(actor);

            if (!gContext.MatchControllerRegulation && actor->IsA(SDK::AMatchController_Regulation_C::StaticClass()))
                gContext.MatchControllerRegulation = static_cast<SDK::AMatchController_Regulation_C*>(actor);

            if (gContext.MatchControllerIndoor && gContext.MatchControllerRegulation)
                break;
        }

        // Atualiza o estado de SingleKeeper com base no controlador encontrado
        if (gContext.MatchControllerRegulation)
        {
            gContext.SingleKeeperAtivo = gContext.MatchControllerRegulation->SingleKeeper;
        }
        else if (gContext.MatchControllerIndoor)
        {
            gContext.SingleKeeperAtivo = gContext.MatchControllerIndoor->SingleKeeper;
        }
    }

    return true;
}
