// === game_pointers.cpp ===

#include "game_pointers.hpp"
#include "SDK.hpp"
#include <cmath>
#include <mutex>

static GamePointers g_Ptrs;
static std::mutex g_Mutex;

GamePointers GetCurrentGamePointers()
{
    std::scoped_lock lock(g_Mutex);
    return g_Ptrs;
}

SDK::UWorld* GetRobustWorld()
{
    if (SDK::Offsets::GWorld != 0)
    {
        uintptr_t imageBase = SDK::InSDKUtils::GetImageBase();
        auto worldPtr = reinterpret_cast<SDK::UWorld**>(imageBase + SDK::Offsets::GWorld);
        if (worldPtr && *worldPtr)
            return *worldPtr;
    }

    SDK::UEngine* engine = SDK::UEngine::GetEngine();
    if (engine && engine->GameViewport && engine->GameViewport->World)
        return engine->GameViewport->World;

    return nullptr;
}

SDK::ASoccerBall_C* FindSoccerBall(SDK::UWorld* world)
{
    if (!world || !world->PersistentLevel) return nullptr;

    auto& actors = world->PersistentLevel->Actors;
    for (int i = 0; i < actors.Num(); ++i)
    {
        auto* actor = actors[i];
        if (actor && actor->IsA(SDK::ASoccerBall_C::StaticClass()))
            return static_cast<SDK::ASoccerBall_C*>(actor);
    }
    return nullptr;
}

void AtualizarGamePointers()
{
    std::scoped_lock lock(g_Mutex);
    g_Ptrs = {};

    g_Ptrs.World = GetRobustWorld();
    if (!g_Ptrs.World) return;

    g_Ptrs.GameInstance = g_Ptrs.World->OwningGameInstance;
    if (!g_Ptrs.GameInstance) return;

    const auto& players = g_Ptrs.GameInstance->LocalPlayers;
    if (players.Num() == 0 || !players[0]) return;

    g_Ptrs.LocalPlayer = players[0];
    g_Ptrs.Controller = g_Ptrs.LocalPlayer->PlayerController;
    if (!g_Ptrs.Controller) return;

    g_Ptrs.Character = static_cast<SDK::ASP_Character_C*>(g_Ptrs.Controller->AcknowledgedPawn);
    g_Ptrs.SoccerBall = FindSoccerBall(g_Ptrs.World);
}

float CalcularDistanciaMetros(const SDK::FVector& a, const SDK::FVector& b)
{
    float dx = a.X - b.X;
    float dy = a.Y - b.Y;
    float dz = a.Z - b.Z;
    return std::sqrt(dx * dx + dy * dy + dz * dz) / 100.0f;
}

float CalcularVelocidade(const SDK::FVector& velocity)
{
    return std::sqrt(velocity.X * velocity.X + velocity.Y * velocity.Y + velocity.Z * velocity.Z) / 100.0f;
}

// === Adicionado para inicialização explícita ===
void InitializeGamePointers()
{
    AtualizarGamePointers();
}
