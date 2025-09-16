#pragma once

#include <Windows.h>
#include <mutex>
#include "SDK.hpp"

struct GamePointers
{
    SDK::UWorld* World = nullptr;
    SDK::UGameInstance* GameInstance = nullptr;
    SDK::ULocalPlayer* LocalPlayer = nullptr;
    SDK::APlayerController* Controller = nullptr;
    SDK::ASP_Character_C* Character = nullptr;
    SDK::ASoccerBall_C* SoccerBall = nullptr;
};

// Inicializa os ponteiros na carga do módulo (chamada única recomendada)
void InitializeGamePointers();

// Atualiza os ponteiros de jogo (seguro para múltiplas threads)
void AtualizarGamePointers();

// Retorna uma cópia segura dos ponteiros atuais
GamePointers GetCurrentGamePointers();

// Calcula a distância em metros entre dois pontos
float CalcularDistanciaMetros(const SDK::FVector& a, const SDK::FVector& b);

// Calcula a velocidade em m/s a partir de um vetor
float CalcularVelocidade(const SDK::FVector& velocity);
