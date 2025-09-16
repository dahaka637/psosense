#include "imgui.h"
#include "imgui_style.hpp"

void ApplyCustomImGuiStyle()
{
    ImGuiStyle& style = ImGui::GetStyle();

    // Estrutura visual
    style.WindowRounding = 6.0f;
    style.FrameRounding = 4.0f;
    style.PopupRounding = 4.0f;
    style.GrabRounding = 3.0f;
    style.ScrollbarRounding = 4.0f;

    style.WindowBorderSize = 1.0f;
    style.FrameBorderSize = 1.0f;
    style.PopupBorderSize = 1.0f;

    style.WindowPadding = ImVec2(12, 10);
    style.FramePadding = ImVec2(10, 6);
    style.ItemSpacing = ImVec2(10, 6);
    style.ItemInnerSpacing = ImVec2(6, 6);
    style.IndentSpacing = 20.0f;

    ImVec4* colors = style.Colors;

    // Paleta "Inferno Hacker"
    colors[ImGuiCol_Text] = ImVec4(0.96f, 0.96f, 0.96f, 1.00f);             // branco gelo
    colors[ImGuiCol_TextDisabled] = ImVec4(0.50f, 0.48f, 0.48f, 1.00f);     // cinza morto

    colors[ImGuiCol_WindowBg] = ImVec4(0.05f, 0.01f, 0.01f, 1.00f);         // preto profundo com tom vermelho
    colors[ImGuiCol_ChildBg] = ImVec4(0.08f, 0.02f, 0.02f, 1.00f);
    colors[ImGuiCol_PopupBg] = ImVec4(0.10f, 0.02f, 0.02f, 0.95f);

    colors[ImGuiCol_Border] = ImVec4(0.50f, 0.00f, 0.00f, 0.60f);           // vermelho escuro translúcido
    colors[ImGuiCol_BorderShadow] = ImVec4(0.0f, 0.0f, 0.0f, 0.0f);

    colors[ImGuiCol_FrameBg] = ImVec4(0.15f, 0.04f, 0.04f, 1.00f);
    colors[ImGuiCol_FrameBgHovered] = ImVec4(0.25f, 0.05f, 0.05f, 1.00f);
    colors[ImGuiCol_FrameBgActive] = ImVec4(0.30f, 0.05f, 0.05f, 1.00f);

    colors[ImGuiCol_TitleBg] = ImVec4(0.10f, 0.01f, 0.01f, 1.00f);
    colors[ImGuiCol_TitleBgActive] = ImVec4(0.20f, 0.00f, 0.00f, 1.00f);
    colors[ImGuiCol_TitleBgCollapsed] = ImVec4(0.06f, 0.00f, 0.00f, 0.60f);

    colors[ImGuiCol_ScrollbarBg] = ImVec4(0.10f, 0.00f, 0.00f, 1.00f);
    colors[ImGuiCol_ScrollbarGrab] = ImVec4(0.60f, 0.00f, 0.00f, 0.6f);
    colors[ImGuiCol_ScrollbarGrabHovered] = ImVec4(0.80f, 0.10f, 0.10f, 0.8f);
    colors[ImGuiCol_ScrollbarGrabActive] = ImVec4(1.00f, 0.20f, 0.20f, 1.0f);

    colors[ImGuiCol_CheckMark] = ImVec4(1.00f, 0.15f, 0.15f, 1.00f);
    colors[ImGuiCol_SliderGrab] = ImVec4(0.90f, 0.20f, 0.20f, 0.85f);
    colors[ImGuiCol_SliderGrabActive] = ImVec4(1.00f, 0.30f, 0.30f, 1.00f);

    colors[ImGuiCol_Button] = ImVec4(0.70f, 0.10f, 0.10f, 0.7f);
    colors[ImGuiCol_ButtonHovered] = ImVec4(0.90f, 0.10f, 0.10f, 1.00f);
    colors[ImGuiCol_ButtonActive] = ImVec4(1.00f, 0.00f, 0.00f, 1.00f);  // vermelho intenso

    colors[ImGuiCol_Header] = ImVec4(0.35f, 0.05f, 0.05f, 0.55f);
    colors[ImGuiCol_HeaderHovered] = ImVec4(0.50f, 0.10f, 0.10f, 0.80f);
    colors[ImGuiCol_HeaderActive] = ImVec4(0.70f, 0.10f, 0.10f, 1.00f);

    colors[ImGuiCol_Separator] = ImVec4(0.30f, 0.00f, 0.00f, 0.60f);
    colors[ImGuiCol_SeparatorHovered] = ImVec4(0.80f, 0.10f, 0.10f, 0.80f);
    colors[ImGuiCol_SeparatorActive] = ImVec4(1.00f, 0.20f, 0.20f, 1.00f);

    colors[ImGuiCol_ResizeGrip] = ImVec4(0.80f, 0.00f, 0.00f, 0.60f);
    colors[ImGuiCol_ResizeGripHovered] = ImVec4(1.00f, 0.10f, 0.10f, 0.80f);
    colors[ImGuiCol_ResizeGripActive] = ImVec4(1.00f, 0.25f, 0.25f, 1.00f);

    colors[ImGuiCol_TextSelectedBg] = ImVec4(0.80f, 0.00f, 0.00f, 0.60f);
    colors[ImGuiCol_DragDropTarget] = ImVec4(1.00f, 0.80f, 0.00f, 0.90f);
    colors[ImGuiCol_NavHighlight] = ImVec4(1.00f, 0.00f, 0.00f, 0.80f);
    colors[ImGuiCol_NavWindowingHighlight] = ImVec4(1.00f, 0.30f, 0.30f, 0.70f);

    // Fonte mais agressiva se quiser adicionar futuramente
    // ImGui::GetIO().FontGlobalScale = 1.1f;
}
