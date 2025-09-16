#pragma once
#include <atomic>

// Inicializa o hook no Present do DirectX 11
void** GetPresentVTable();
void HookPresent();

// Estado da interface ImGui
extern bool imgui_initialized;
extern std::atomic_bool g_ShowWatermark;
extern std::atomic_bool g_ShowMenu;

// Controle da watermark
void EnableWatermark();
void DisableWatermark();

// Interface ImGui personalizada
void RenderImGuiInterface();
