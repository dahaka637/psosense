#include "imgui.h"
#include "auto_gk.hpp"
#include "dx11_hook.hpp"
#include "menu.hpp"
#include <Windows.h>
#include <iostream>
#include <chrono>
#include <thread>

extern bool g_ShowUI;
extern float g_MinCaptureRange;
extern float g_MaxCaptureRange;

bool g_EnableForceCatchKey = false;
int g_ForceCatchKey = 'F';
bool g_WaitingForKey = false;
bool g_ForceCatchOnlyIfInRange = true;

char g_feedbackText[64] = "";
float g_feedbackTimer = 0.0f;

const char* GetKeyName(int keycode) {
    static char name[64] = {};
    GetKeyNameTextA(MapVirtualKeyA(keycode, MAPVK_VK_TO_VSC) << 16, name, sizeof(name));
    return *name ? name : "Unknown";
}

void CheckForceCatchKeybind() {
    static bool wasPressed = false;
    static std::chrono::steady_clock::time_point lastPressTime = std::chrono::steady_clock::now();

    if (!g_EnableForceCatchKey)
        return;

    SHORT state = GetAsyncKeyState(g_ForceCatchKey);
    bool isPressedNow = (state & 0x8000) != 0;

    if (isPressedNow && !wasPressed) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastPressTime);

        if (elapsed.count() >= 1000) {
            lastPressTime = now;
            
            std::this_thread::sleep_for(std::chrono::milliseconds(AutoGK::g_ForceCatchDelayMs));
            AutoGK::ForceCatchBall();

            snprintf(g_feedbackText, sizeof(g_feedbackText), "Manual Catch (key) executed!");
            g_feedbackTimer = 2.5f;
        }
    }

    wasPressed = isPressedNow;
}

void RenderImGuiInterface()
{
    CheckForceCatchKeybind();

    ImGui::Begin("PSOSense - AutoGK", nullptr, ImGuiWindowFlags_AlwaysAutoResize);

    ImGui::TextColored(AutoGK::IsRunning() ? ImVec4(0.1f, 1.0f, 0.1f, 1.0f) : ImVec4(1.0f, 0.1f, 0.1f, 1.0f),
        AutoGK::IsRunning() ? "AutoGK: ACTIVE" : "AutoGK: INACTIVE");

    if (ImGui::Button(AutoGK::IsRunning() ? "Stop AutoGK" : "Start AutoGK"))
        AutoGK::Toggle();

    ImGui::SeparatorText("Capture Range");
    ImGui::SliderFloat("Min Capture Distance", &g_MinCaptureRange, 0.5f, 20.0f);
    ImGui::SliderFloat("Max Capture Distance", &g_MaxCaptureRange, 1.0f, 30.0f);

    if (ImGui::Button("Update Range")) {
        AutoGK::SetRange(g_MinCaptureRange, g_MaxCaptureRange);
        snprintf(g_feedbackText, sizeof(g_feedbackText), "Range updated successfully!");
        g_feedbackTimer = 2.5f;
    }

    ImGui::SeparatorText("Manual Catch");
    if (ImGui::Button("Force Catch Ball (Manual)")) {
        AutoGK::ForceCatchBall();
        snprintf(g_feedbackText, sizeof(g_feedbackText), "Manual Catch executed!");
        g_feedbackTimer = 2.5f;
    }

    ImGui::Checkbox("Enable Keybind for Force Catch", &g_EnableForceCatchKey);
    ImGui::SameLine();
    ImGui::Checkbox("Use Distance Limit", &g_ForceCatchOnlyIfInRange);
    AutoGK::g_UseDistanceForManualCatch = g_ForceCatchOnlyIfInRange;

    if (g_EnableForceCatchKey) {
        if (g_WaitingForKey) {
            ImGui::Text("Press any key...");
            for (int vk = 1; vk <= 255; ++vk) {
                if (GetAsyncKeyState(vk) & 0x8000) {
                    g_ForceCatchKey = vk;
                    g_WaitingForKey = false;
                    snprintf(g_feedbackText, sizeof(g_feedbackText), "Keybind set to: %s", GetKeyName(vk));
                    g_feedbackTimer = 2.5f;
                    break;
                }
            }
        }
        else {
            ImGui::Text("Key: %s", GetKeyName(g_ForceCatchKey));
            ImGui::SameLine();
            if (ImGui::Button("Change Key")) {
                g_WaitingForKey = true;
            }
        }

        ImGui::SliderInt("Force Catch Delay (ms)", &AutoGK::g_ForceCatchDelayMs, 0, 1000);
    }

    ImGui::End();

    if (g_ShowWatermark) {
        ImGui::SetNextWindowPos(ImVec2(8, ImGui::GetIO().DisplaySize.y - 30), ImGuiCond_Always);
        ImGui::SetNextWindowBgAlpha(0.0f);
        ImGui::Begin("PSOSenseText", nullptr, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoInputs | ImGuiWindowFlags_NoBackground | ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse | ImGuiWindowFlags_AlwaysAutoResize);
        ImGui::TextColored(ImVec4(0.12f, 0.95f, 0.45f, 1.0f), "PSOSENSE");
        ImGui::SameLine();
        ImGui::TextColored(ImVec4(0.40f, 0.80f, 1.0f, 1.0f), "AUTO-GK");
        ImGui::End();
    }

    if (g_feedbackTimer > 0.0f) {
        g_feedbackTimer -= ImGui::GetIO().DeltaTime;
        ImGui::SetNextWindowPos(ImVec2(ImGui::GetIO().DisplaySize.x - 200, ImGui::GetIO().DisplaySize.y - 50), ImGuiCond_Always);
        ImGui::SetNextWindowBgAlpha(0.7f);
        ImGui::Begin("FeedbackWindow", nullptr, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoFocusOnAppearing | ImGuiWindowFlags_NoNav);
        ImGui::Text("%s", g_feedbackText);
        ImGui::End();
    }
}
