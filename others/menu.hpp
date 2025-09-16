#pragma once


// (Opcional) Expor variáveis globais se usadas externamente
extern bool g_LobbyCrasherActive;
extern int g_CrashIntervalMs;
extern float g_feedbackTimer;
extern char g_feedbackText[64];
extern bool g_ShowWatermark;
void RenderWatermark();
extern void SetAntiKickEnabled(bool enabled);
