#pragma once
#include "SDK.hpp"

struct GameContext
{
    SDK::UWorld* World = nullptr;
    SDK::UGameInstance* GameInstance = nullptr;
    SDK::ULocalPlayer* LocalPlayer = nullptr;
    SDK::APlayerController* Controller = nullptr;
    SDK::ASP_Controller_C* SPController = nullptr;
    SDK::ASP_Character_C* Character = nullptr;
    SDK::AMP_PlayerState_C* PlayerState = nullptr;
    SDK::AGameStateBase* GameState = nullptr;
    SDK::AMP_GameState_C* CustomGameState = nullptr;

    SDK::AMatchController_Indoor_C* MatchControllerIndoor = nullptr;
    SDK::AMatchController_Regulation_C* MatchControllerRegulation = nullptr;

    // Novo campo: estado atual do modo SingleKeeper
    bool SingleKeeperAtivo = false;
};

extern GameContext gContext;

bool InitializeGameContext();
