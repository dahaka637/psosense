#pragma once
#include <atomic>

namespace AutoGK
{
    extern std::atomic<bool> g_UseDistanceForManualCatch;

    // 🔽 Adicione esta linha:
    extern int g_ForceCatchDelayMs;

    void Start();
    void Toggle();
    bool IsRunning();
    void SetRange(float minMetros, float maxMetros);
    void ForceCatchBall();
}
