#pragma once

// Inicializa e atualiza os ponteiros do jogo (World, Controller, Character, etc.)
bool InitializeGameContext();

// Executa a função InitiateSwap() no PlayerState do personagem
void ExecuteInitiateSwap();

void ExecuteSpawnBall();

void ExecuteForceResetMatch();

void ExecuteToggleSingleKeeper();

void ExecuteEnableAntiKick();

void ExecuteDisableAntiKick();

void ExecuteEnableTouchSlow();

void ExecuteDisableTouchSlow();