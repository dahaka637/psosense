// function_calls.cpp
#include "game_context.hpp"
#include <iostream>
#include "antikick.hpp"

// Verifica se a função obtida é válida (endereço plausível)
inline bool IsFunctionValid(SDK::UFunction* func)
{
    return func && reinterpret_cast<uintptr_t>(func) > 0x10000;
}

// Troca de time (swap)
void ExecuteInitiateSwap()
{
    if (!InitializeGameContext())
    {
        std::cout << "[ERRO] Falha ao inicializar o contexto do jogo.\n";
        return;
    }

    if (!gContext.PlayerState)
    {
        std::cout << "[ERRO] PlayerState nulo.\n";
        return;
    }

    static SDK::UFunction* swapFunc = nullptr;
    if (!swapFunc)
        swapFunc = gContext.PlayerState->Class->GetFunction("MP_PlayerState_C", "InitiateSwap");

    if (!IsFunctionValid(swapFunc))
    {
        std::cout << "[ERRO] Função InitiateSwap inválida ou não encontrada.\n";
        return;
    }

    std::cout << "[CALL] Executando InitiateSwap()...\n";
    gContext.PlayerState->ProcessEvent(swapFunc, nullptr);
    std::cout << "[CALL] InitiateSwap() concluído.\n";
}

// Criação e destruição da bola
void ExecuteSpawnBall()
{
    if (!InitializeGameContext())
    {
        std::cout << "[ERRO] Falha ao inicializar o contexto do jogo.\n";
        return;
    }

    if (!gContext.Character)
    {
        std::cout << "[ERRO] Character nulo.\n";
        return;
    }

    // Destroy bola anterior
    static SDK::UFunction* destroyFunc = nullptr;
    if (!destroyFunc)
        destroyFunc = gContext.Character->Class->GetFunction("SP_Character_C", "DestroyPersonalBall");

    if (IsFunctionValid(destroyFunc))
    {
        std::cout << "[CALL] Destruindo bola antiga (se houver)...\n";
        gContext.Character->ProcessEvent(destroyFunc, nullptr);
    }
    else
    {
        std::cout << "[WARN] DestroyPersonalBall não disponível.\n";
    }

    // Spawn nova bola
    static SDK::UFunction* spawnFunc = nullptr;
    if (!spawnFunc)
        spawnFunc = gContext.Character->Class->GetFunction("SP_Character_C", "SpawnBall");

    if (IsFunctionValid(spawnFunc))
    {
        std::cout << "[CALL] Spawnando nova bola...\n";
        gContext.Character->ProcessEvent(spawnFunc, nullptr);
        std::cout << "[CALL] Bola criada com sucesso!\n";
    }
    else
    {
        std::cout << "[ERRO] SpawnBall não disponível ou inválido.\n";
    }
}

void ExecuteForceResetMatch()
{
    if (!InitializeGameContext())
    {
        std::cout << "[ERRO] Falha ao inicializar o contexto do jogo.\n";
        return;
    }

    if (!gContext.SPController || !gContext.CustomGameState)
    {
        std::cout << "[ERRO] SPController ou GameState inválido.\n";
        return;
    }

    int32_t matchState = gContext.CustomGameState->MatchState;
    std::cout << "[DEBUG] Estado atual da partida (MatchState): " << matchState << "\n";

    if (matchState == 0)
    {
        // Iniciar partida
        static SDK::UFunction* startFunc = nullptr;
        if (!startFunc)
            startFunc = gContext.SPController->Class->GetFunction("SP_Controller_C", "CL_Host_ForceStartMatch");

        if (!IsFunctionValid(startFunc))
        {
            std::cout << "[ERRO] Função CL_Host_ForceStartMatch inválida.\n";
            return;
        }

        std::cout << "[CALL] Iniciando partida...\n";
        gContext.SPController->ProcessEvent(startFunc, nullptr);
        std::cout << "[CALL] Partida iniciada com sucesso!\n";
    }
    else
    {
        // Reiniciar partida
        static SDK::UFunction* resetFunc = nullptr;
        if (!resetFunc)
            resetFunc = gContext.SPController->Class->GetFunction("SP_Controller_C", "CL_Host_ForceResetMatch");

        if (!IsFunctionValid(resetFunc))
        {
            std::cout << "[ERRO] Função CL_Host_ForceResetMatch inválida.\n";
            return;
        }

        std::cout << "[CALL] Reiniciando partida...\n";
        gContext.SPController->ProcessEvent(resetFunc, nullptr);
        std::cout << "[CALL] Partida reiniciada com sucesso!\n";
    }
}


// Struct manualmente definida, já que o SDK não fornece
struct SP_Controller_C_CL_Host_SetSingleKeeper
{
    bool SingleKeeper;
};

void ExecuteToggleSingleKeeper()
{
    if (!InitializeGameContext())
    {
        std::cout << "[ERRO] Falha ao inicializar o contexto do jogo.\n";
        return;
    }

    if (!gContext.SPController)
    {
        std::cout << "[ERRO] SPController não encontrado.\n";
        return;
    }

    static SDK::UFunction* toggleFunc = nullptr;
    if (!toggleFunc)
        toggleFunc = gContext.SPController->Class->GetFunction("SP_Controller_C", "CL_Host_SetSingleKeeper");

    if (!IsFunctionValid(toggleFunc))
    {
        std::cout << "[ERRO] Função CL_Host_SetSingleKeeper inválida.\n";
        return;
    }

    // Usa a struct manual declarada acima
    SP_Controller_C_CL_Host_SetSingleKeeper params{};
    params.SingleKeeper = !gContext.SingleKeeperAtivo;

    std::cout << "[CALL] Alternando modo SingleKeeper para: "
        << (params.SingleKeeper ? "ATIVO" : "DESATIVADO") << "\n";

    gContext.SPController->ProcessEvent(toggleFunc, &params);
}

void ExecuteEnableAntiKick()
{
    if (!IsAntiKickEnabled())
    {
        SetAntiKickEnabled(true);
        std::cout << "[CALL] AntiKick ATIVADO.\n";
    }
    else
    {
        std::cout << "[CALL] AntiKick já estava ativado.\n";
    }
}

void ExecuteDisableAntiKick()
{
    if (IsAntiKickEnabled())
    {
        SetAntiKickEnabled(false);
        std::cout << "[CALL] AntiKick DESATIVADO.\n";
    }
    else
    {
        std::cout << "[CALL] AntiKick já estava desativado.\n";
    }
}
