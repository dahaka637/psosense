#include <Windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <iostream>
#include "MinHook/include/MinHook.h"
#include "dx11_hook.hpp"
#include <atomic>

#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "dxgi.lib")

#include "imgui.h"
#include "backends/imgui_impl_dx11.h"
#include "backends/imgui_impl_win32.h"

using Microsoft::WRL::ComPtr;


std::atomic_bool g_ShowWatermark = true;


typedef HRESULT(APIENTRY* PresentFn)(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags);
typedef HRESULT(APIENTRY* ResizeBuffersFn)(IDXGISwapChain* pSwapChain, UINT BufferCount, UINT Width, UINT Height, DXGI_FORMAT NewFormat, UINT SwapChainFlags);

PresentFn oPresent = nullptr;
ResizeBuffersFn oResizeBuffers = nullptr;

bool imgui_initialized = false;
static ID3D11Device* g_pd3dDevice = nullptr;
static ID3D11DeviceContext* g_pd3dDeviceContext = nullptr;
static ID3D11RenderTargetView* g_mainRenderTargetView = nullptr;

static int safe_frame_delay = 0;

void CreateRenderTarget(IDXGISwapChain* pSwapChain)
{
    if (g_mainRenderTargetView) {
        g_mainRenderTargetView->Release();
        g_mainRenderTargetView = nullptr;
    }

    ID3D11Texture2D* pBackBuffer = nullptr;
    HRESULT hr = pSwapChain->GetBuffer(0, __uuidof(ID3D11Texture2D), (LPVOID*)&pBackBuffer);
    if (SUCCEEDED(hr) && pBackBuffer)
    {
        hr = g_pd3dDevice->CreateRenderTargetView(pBackBuffer, nullptr, &g_mainRenderTargetView);
        pBackBuffer->Release();
    }
}

HRESULT APIENTRY HookedResizeBuffers(IDXGISwapChain* pSwapChain, UINT BufferCount, UINT Width, UINT Height, DXGI_FORMAT NewFormat, UINT SwapChainFlags)
{
    if (g_mainRenderTargetView)
    {
        g_mainRenderTargetView->Release();
        g_mainRenderTargetView = nullptr;
    }

    if (g_pd3dDeviceContext)
    {
        g_pd3dDeviceContext->OMSetRenderTargets(0, nullptr, nullptr);
    }

    return oResizeBuffers(pSwapChain, BufferCount, Width, Height, NewFormat, SwapChainFlags);
}

HRESULT APIENTRY HookedPresent(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags)
{
    if (!imgui_initialized)
    {
        safe_frame_delay++;
        if (safe_frame_delay < 60)
            return oPresent(pSwapChain, SyncInterval, Flags);

        DXGI_SWAP_CHAIN_DESC sd;
        if (FAILED(pSwapChain->GetDesc(&sd)) || !sd.OutputWindow)
            return oPresent(pSwapChain, SyncInterval, Flags);

        HWND hwnd = sd.OutputWindow;
        if (FAILED(pSwapChain->GetDevice(__uuidof(ID3D11Device), (void**)&g_pd3dDevice)))
            return oPresent(pSwapChain, SyncInterval, Flags);

        g_pd3dDevice->GetImmediateContext(&g_pd3dDeviceContext);

        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGui_ImplWin32_Init(hwnd);
        ImGui_ImplDX11_Init(g_pd3dDevice, g_pd3dDeviceContext);

        ImFontConfig font_cfg;
        font_cfg.SizePixels = 28.0f;
        font_cfg.OversampleH = 3;
        font_cfg.OversampleV = 3;
        ImGui::GetIO().Fonts->AddFontDefault(&font_cfg);

        CreateRenderTarget(pSwapChain);
        imgui_initialized = true;
    }

    if (!g_mainRenderTargetView)
        CreateRenderTarget(pSwapChain);

    g_pd3dDeviceContext->OMSetRenderTargets(1, &g_mainRenderTargetView, nullptr);

    ImGui_ImplDX11_NewFrame();
    ImGui_ImplWin32_NewFrame();
    ImGui::NewFrame();

    // Exibe a watermark se estiver ativada
    if (g_ShowWatermark)
    {
        ImGui::SetNextWindowPos(ImVec2(8, ImGui::GetIO().DisplaySize.y - 30), ImGuiCond_Always);
        ImGui::SetNextWindowBgAlpha(0.0f);

        ImGui::Begin("PSOSenseText", nullptr,
            ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_AlwaysAutoResize |
            ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoInputs | ImGuiWindowFlags_NoBackground);

        ImDrawList* drawList = ImGui::GetWindowDrawList();
        ImVec2 pos = ImGui::GetCursorScreenPos();

        const char* pso = "pso";
        const char* sense = "sense";

        ImVec4 green = ImVec4(0.12f, 0.95f, 0.45f, 1.0f);
        ImVec4 white = ImVec4(1.0f, 1.0f, 1.0f, 1.0f);

        ImFont* font = ImGui::GetFont();
        float fontSize = font->FontSize * 0.6f;

        ImVec2 size_pso = font->CalcTextSizeA(fontSize, FLT_MAX, 0.0f, pso);
        ImVec2 size_sense = font->CalcTextSizeA(fontSize, FLT_MAX, 0.0f, sense);
        ImVec2 pos_sense = ImVec2(pos.x + size_pso.x + 2.0f, pos.y);

        drawList->AddText(font, fontSize, pos, ImGui::ColorConvertFloat4ToU32(green), pso);
        drawList->AddText(font, fontSize, pos_sense, ImGui::ColorConvertFloat4ToU32(white), sense);

        ImGui::Dummy(ImVec2(size_pso.x + size_sense.x + 2, size_pso.y));
        ImGui::End();
    }

    ImGui::Render();
    ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

    return oPresent(pSwapChain, SyncInterval, Flags);
}

void** GetPresentVTable()
{
    DXGI_SWAP_CHAIN_DESC sd = {};
    sd.BufferCount = 1;
    sd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    sd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    sd.OutputWindow = GetForegroundWindow();
    sd.SampleDesc.Count = 1;
    sd.Windowed = TRUE;
    sd.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;

    D3D_FEATURE_LEVEL featureLevel;
    const D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_11_0 };

    ComPtr<ID3D11Device> pDevice;
    ComPtr<ID3D11DeviceContext> pContext;
    ComPtr<IDXGISwapChain> pSwapChain;

    HRESULT hr = D3D11CreateDeviceAndSwapChain(
        nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, 0,
        featureLevels, 1, D3D11_SDK_VERSION, &sd,
        pSwapChain.GetAddressOf(), pDevice.GetAddressOf(), &featureLevel, pContext.GetAddressOf()
    );

    if (FAILED(hr)) return nullptr;

    void** vTable = *reinterpret_cast<void***>(pSwapChain.Get());
    return vTable;
}

void HookPresent()
{
    void** vtable = GetPresentVTable();
    if (!vtable) return;

    void* pPresentAddr = vtable[8];
    void* pResizeBuffersAddr = vtable[13];

    if (MH_Initialize() != MH_OK && MH_Initialize() != MH_ERROR_ALREADY_INITIALIZED)
        return;

    if (MH_CreateHook(pPresentAddr, &HookedPresent, reinterpret_cast<void**>(&oPresent)) != MH_OK)
        return;

    MH_EnableHook(pPresentAddr);

    if (MH_CreateHook(pResizeBuffersAddr, &HookedResizeBuffers, reinterpret_cast<void**>(&oResizeBuffers)) != MH_OK)
        return;

    MH_EnableHook(pResizeBuffersAddr);
}


void EnableWatermark() {
    g_ShowWatermark = true;
    std::cout << "[WATERMARK] Watermark ativada.\n";
}

void DisableWatermark() {
    g_ShowWatermark = false;
    std::cout << "[WATERMARK] Watermark desativada.\n";
}
