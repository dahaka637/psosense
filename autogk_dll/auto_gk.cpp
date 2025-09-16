// auto_gk.cpp
#include <Windows.h>
#include <iostream>
#include <thread>
#include <atomic>
#include <chrono>
#include <mutex>
#include <exception>
#include "menu.hpp"
#include "SDK.hpp"
#include "game_pointers.hpp"
#include "auto_gk.hpp"

namespace AutoGK
{
    std::atomic<bool> Ativo = false;
    std::atomic<float> MinRange = 0.5f;
    std::atomic<float> MaxRange = 30.0f;
    std::atomic<bool> g_UseDistanceForManualCatch = false;
    int g_ForceCatchDelayMs = 0;


    constexpr uintptr_t Offset_Position = 0x0694;
    constexpr uintptr_t Offset_CanCatch = 0x0709;

    std::mutex g_CatchCooldownMutex;
    std::chrono::steady_clock::time_point g_LastCatchTime = std::chrono::steady_clock::now() - std::chrono::seconds(2);
    constexpr int g_CatchCooldownMs = 1800;

    std::mutex g_GamePointersMutex;
    GamePointers g_CachedPointers;
    std::chrono::steady_clock::time_point g_LastPointerUpdate = std::chrono::steady_clock::now() - std::chrono::seconds(10);

    void UpdateCachedPointers()
    {
        std::lock_guard<std::mutex> lock(g_GamePointersMutex);
        AtualizarGamePointers();
        g_CachedPointers = GetCurrentGamePointers();
        g_LastPointerUpdate = std::chrono::steady_clock::now();
    }

    GamePointers GetValidPointers()
    {
        std::lock_guard<std::mutex> lock(g_GamePointersMutex);
        return g_CachedPointers;
    }

    bool ArePointersValid(const GamePointers& ptrs)
    {
        return ptrs.Character && ptrs.SoccerBall && ptrs.Character->RootComponent && ptrs.SoccerBall->RootComponent;
    }

    bool IsGoalkeeper(SDK::ASP_Character_C* character)
    {
        if (!character) return false;
        try {
            int32_t pos = *reinterpret_cast<int32_t*>(reinterpret_cast<uintptr_t>(character) + Offset_Position);
            return pos == 0;
        }
        catch (...) { return false; }
    }

    bool CanCatch(SDK::ASP_Character_C* character)
    {
        if (!character) return false;
        try {
            return *reinterpret_cast<bool*>(reinterpret_cast<uintptr_t>(character) + Offset_CanCatch);
        }
        catch (...) { return false; }
    }

    bool IsCooldownActive()
    {
        std::lock_guard<std::mutex> lock(g_CatchCooldownMutex);
        auto now = std::chrono::steady_clock::now();
        return std::chrono::duration_cast<std::chrono::milliseconds>(now - g_LastCatchTime).count() < g_CatchCooldownMs;
    }

    void RegisterCatchExecution()
    {
        std::lock_guard<std::mutex> lock(g_CatchCooldownMutex);
        g_LastCatchTime = std::chrono::steady_clock::now();
    }

    void ExecuteGkEnterCatch(SDK::ASP_Character_C* character, SDK::ASoccerBall_C* ball)
    {
        if (!character || !ball || IsCooldownActive()) return;
        try {
            character->GkEnterCatch(character, ball, 0.0f, 0.0f);
            RegisterCatchExecution();
            std::cout << "[AutoGK] GkEnterCatch executado.\n";
        }
        catch (...) {
            std::cerr << "[AutoGK] Erro ao executar GkEnterCatch.\n";
        }
    }

    void AutoGKThread()
    {
        try {
            SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_ABOVE_NORMAL);

            while (Ativo)
            {
                if (std::chrono::steady_clock::now() - g_LastPointerUpdate >= std::chrono::seconds(5))
                    UpdateCachedPointers();

                GamePointers ptrs = GetValidPointers();
                if (!ArePointersValid(ptrs)) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                    continue;
                }

                if (!IsGoalkeeper(ptrs.Character) || !CanCatch(ptrs.Character)) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(50));
                    continue;
                }

                float distancia = CalcularDistanciaMetros(ptrs.Character->RootComponent->RelativeLocation,
                    ptrs.SoccerBall->RootComponent->RelativeLocation);
                float velocidade = CalcularVelocidade(ptrs.SoccerBall->RootComponent->ComponentVelocity);
                float alcance = MinRange.load() + std::min<float>(velocidade * 0.5f, MaxRange.load());

                if (distancia <= alcance)
                    ExecuteGkEnterCatch(ptrs.Character, ptrs.SoccerBall);

                std::this_thread::sleep_for(std::chrono::milliseconds(50));
            }

            std::cout << "[AutoGK] Desativado.\n";
        }
        catch (const std::exception& ex) {
            std::cerr << "[AutoGK] Excecao na thread: " << ex.what() << "\n";
        }
        catch (...) {
            std::cerr << "[AutoGK] Erro inesperado na thread.\n";
        }
    }

    void Start()
    {
        if (!Ativo)
        {
            Ativo = true;
            UpdateCachedPointers();
            std::thread(AutoGKThread).detach();
            std::cout << "[AutoGK] Iniciado automaticamente.\n";
        }
    }

    void Toggle()
    {
        Ativo = !Ativo;
        if (Ativo) {
            UpdateCachedPointers();
            std::thread(AutoGKThread).detach();
            std::cout << "[AutoGK] Ativado por toggle.\n";
        }
        else {
            std::cout << "[AutoGK] Desativando...\n";
        }
    }

    bool IsRunning()
    {
        return Ativo;
    }

    void SetRange(float minMetros, float maxMetros)
    {
        if (minMetros < 0.0f) minMetros = 0.0f;
        if (maxMetros < 1.0f) maxMetros = 1.0f;
        if (minMetros > maxMetros) std::swap(minMetros, maxMetros);

        MinRange = minMetros;
        MaxRange = maxMetros;

        std::cout << "[AutoGK] Novo alcance configurado: Min = " << MinRange << " | Max = " << MaxRange << "\n";
    }

    void ForceCatchBall()
    {
        std::thread([] {
            try {
                if (g_ForceCatchDelayMs > 0)
                    std::this_thread::sleep_for(std::chrono::milliseconds(g_ForceCatchDelayMs));

                UpdateCachedPointers();
                GamePointers ptrs = GetValidPointers();
                if (!ArePointersValid(ptrs)) return;

                if (g_UseDistanceForManualCatch) {
                    float distancia = CalcularDistanciaMetros(ptrs.Character->RootComponent->RelativeLocation,
                        ptrs.SoccerBall->RootComponent->RelativeLocation);
                    float velocidade = CalcularVelocidade(ptrs.SoccerBall->RootComponent->ComponentVelocity);
                    float alcance = MinRange.load() + std::min<float>(velocidade * 0.5f, MaxRange.load());
                    if (distancia > alcance) {
                        std::cout << "[AutoGK] Manual Catch cancelado: fora do alcance definido.\n";
                        return;
                    }
                }

                ExecuteGkEnterCatch(ptrs.Character, ptrs.SoccerBall);
            }
            catch (...) {
                std::cerr << "[AutoGK] Falha ao executar captura forcada.\n";
            }
            }).detach();
    }
}