#pragma once

// Inicializa o sistema de bloqueio de funções (hook em ProcessEvent)
void InitializeFunctionBlocker();

// Controle individual de funções bloqueáveis
void SetAntiKickEnabled(bool enabled);
bool IsAntiKickEnabled();

void SetTouchSlowEnabled(bool enabled);
bool IsTouchSlowEnabled();

// Adicione aqui mais funções caso queira permitir controle individual
