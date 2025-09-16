#pragma once

// Inicializa o hook anti-kick
void InitializeAntiKick();

// Ativa/desativa proteção contra kick
void SetAntiKickEnabled(bool enabled);

// Consulta se está ativo
bool IsAntiKickEnabled();
