#include "imgui.h"
#include <Windows.h>
#include <string>
#include <cmath>

// Estado da animação
static float animationTimer = 0.0f;
static float pulseTimer = 0.0f;
static int visibleLetters = 0;
static int pulseCount = 0;
static int completedLoops = 0;
static bool animationDone = false;

const char* fullText = "PSOSENSE Spoofer";
static const float letterDelay = 0.08f;   // tempo entre letras
static const float pulseInterval = 0.6f;  // tempo entre pulsares

void RenderWatermark()
{
    if (animationDone) return;

    ImDrawList* draw_list = ImGui::GetBackgroundDrawList();
    ImVec2 pos = ImVec2(10, 10);

    float deltaTime = ImGui::GetIO().DeltaTime;
    animationTimer += deltaTime;

    int totalLength = (int)strlen(fullText);
    int targetVisible = (int)(animationTimer / letterDelay);

    if (visibleLetters < totalLength)
    {
        visibleLetters = min(targetVisible, totalLength);
    }
    else if (pulseCount < 3)
    {
        pulseTimer += deltaTime;
        if (pulseTimer >= pulseInterval)
        {
            pulseTimer = 0.0f;
            pulseCount++;
        }
    }
    else
    {
        completedLoops++;
        if (completedLoops >= 3)
        {
            animationDone = true;
            return;
        }
        // reinicia o ciclo
        animationTimer = 0.0f;
        pulseTimer = 0.0f;
        visibleLetters = 0;
        pulseCount = 0;
        return;
    }

    std::string textToShow(fullText, visibleLetters);

    // Oscilação de alpha (fade pulsante)
    float alpha = 1.0f;
    if (visibleLetters >= totalLength && pulseCount < 3)
    {
        alpha = 0.5f + 0.5f * sinf(pulseTimer * 10.0f); // entre 0.0 e 1.0
    }

    ImU32 textColor = ImGui::GetColorU32(ImVec4(0.7f, 0.3f, 1.0f, alpha)); // roxo com fade
    ImU32 outlineColor = IM_COL32(0, 0, 0, (int)(alpha * 255));
    float fontSize = 22.0f;

    for (int dx = -1; dx <= 1; ++dx)
    {
        for (int dy = -1; dy <= 1; ++dy)
        {
            if (dx != 0 || dy != 0)
                draw_list->AddText(nullptr, fontSize, ImVec2(pos.x + dx, pos.y + dy), outlineColor, textToShow.c_str());
        }
    }

    draw_list->AddText(nullptr, fontSize, pos, textColor, textToShow.c_str());
}
