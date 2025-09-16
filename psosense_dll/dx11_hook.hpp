#pragma once
#include <atomic>

// Retorna a vtable do IDXGISwapChain
void** GetPresentVTable();
void HookPresent();
extern bool imgui_initialized;



extern std::atomic_bool g_ShowWatermark;
void EnableWatermark();
void DisableWatermark();
