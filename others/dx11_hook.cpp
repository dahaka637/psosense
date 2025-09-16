#include "menu.hpp"
#include "dx11_hook.hpp"
#include "imgui_style.hpp"
#include "game_context.hpp"

#include "MinHook/include/MinHook.h"
#include <Windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <iostream>
#include <atomic>

#include "imgui.h"
#include "backends/imgui_impl_dx11.h"
#include "backends/imgui_impl_win32.h"

#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "dxgi.lib")
extern LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);


using Microsoft::WRL::ComPtr;

// === Variáveis Globais ===
bool g_ShowUI = false;
bool imgui_initialized = false;

static ID3D11Device* g_pd3dDevice = nullptr;
static ID3D11DeviceContext* g_pd3dDeviceContext = nullptr;
static ID3D11RenderTargetView* g_mainRenderTargetView = nullptr;
static HWND g_hWnd = nullptr;
static WNDPROC oWndProc = nullptr;

static int frame_delay = 0;

typedef HRESULT(APIENTRY* PresentFn)(IDXGISwapChain*, UINT, UINT);
typedef HRESULT(APIENTRY* ResizeBuffersFn)(IDXGISwapChain*, UINT, UINT, UINT, DXGI_FORMAT, UINT);

PresentFn oPresent = nullptr;
ResizeBuffersFn oResizeBuffers = nullptr;

// === WndProc Hook ===
LRESULT CALLBACK WndProcHook(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
    if (g_ShowUI) {
        ImGuiIO& io = ImGui::GetIO();
        if (ImGui_ImplWin32_WndProcHandler(hWnd, uMsg, wParam, lParam)) {
            if (io.WantCaptureMouse || io.WantCaptureKeyboard)
                return true;
        }
    }

    return CallWindowProc(oWndProc, hWnd, uMsg, wParam, lParam);
}

// === Render Target ===
void CreateRenderTarget(IDXGISwapChain* pSwapChain)
{
    if (g_mainRenderTargetView) {
        g_mainRenderTargetView->Release();
        g_mainRenderTargetView = nullptr;
    }

    ID3D11Texture2D* pBackBuffer = nullptr;
    if (SUCCEEDED(pSwapChain->GetBuffer(0, __uuidof(ID3D11Texture2D), (LPVOID*)&pBackBuffer))) {
        g_pd3dDevice->CreateRenderTargetView(pBackBuffer, nullptr, &g_mainRenderTargetView);
        pBackBuffer->Release();
    }
}

// === Hooks ===
HRESULT APIENTRY HookedResizeBuffers(IDXGISwapChain* pSwapChain, UINT BufferCount, UINT Width, UINT Height, DXGI_FORMAT NewFormat, UINT SwapChainFlags)
{
    if (g_mainRenderTargetView) g_mainRenderTargetView->Release();
    if (g_pd3dDeviceContext) g_pd3dDeviceContext->OMSetRenderTargets(0, nullptr, nullptr);
    return oResizeBuffers(pSwapChain, BufferCount, Width, Height, NewFormat, SwapChainFlags);
}

HRESULT APIENTRY HookedPresent(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags)
{
    if (!imgui_initialized)
    {
        if (++frame_delay < 60)
            return oPresent(pSwapChain, SyncInterval, Flags);

        DXGI_SWAP_CHAIN_DESC sd;
        if (FAILED(pSwapChain->GetDesc(&sd)))
            return oPresent(pSwapChain, SyncInterval, Flags);
        g_hWnd = sd.OutputWindow;

        if (FAILED(pSwapChain->GetDevice(__uuidof(ID3D11Device), (void**)&g_pd3dDevice)))
            return oPresent(pSwapChain, SyncInterval, Flags);
        g_pd3dDevice->GetImmediateContext(&g_pd3dDeviceContext);

        ImGui::CreateContext();
        ImGuiIO& io = ImGui::GetIO(); (void)io;
        io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
        io.ConfigFlags |= ImGuiConfigFlags_NoMouseCursorChange;

        ApplyCustomImGuiStyle();

        ImGui_ImplWin32_Init(g_hWnd);
        oWndProc = (WNDPROC)SetWindowLongPtr(g_hWnd, GWLP_WNDPROC, (LONG_PTR)WndProcHook);
        ImGui_ImplDX11_Init(g_pd3dDevice, g_pd3dDeviceContext);

        CreateRenderTarget(pSwapChain);
        imgui_initialized = true;
    }

    if (!g_mainRenderTargetView)
        CreateRenderTarget(pSwapChain);

    g_pd3dDeviceContext->OMSetRenderTargets(1, &g_mainRenderTargetView, nullptr);

    // Toggle da interface com tecla Insert
    static bool wasInsertPressed = false;
    bool insertPressedNow = GetAsyncKeyState(VK_INSERT) & 0x8000;
    if (insertPressedNow && !wasInsertPressed) {
        g_ShowUI = !g_ShowUI;
        ShowCursor(g_ShowUI);

        if (g_ShowUI) {
            SetCapture(nullptr);
            SetForegroundWindow(g_hWnd);
        }
    }
    wasInsertPressed = insertPressedNow;

    // ImGui Frame
    ImGui_ImplDX11_NewFrame();
    ImGui_ImplWin32_NewFrame();
    ImGui::NewFrame();

    RenderWatermark();
    ImGui::Render();
    ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

    return oPresent(pSwapChain, SyncInterval, Flags);
}

// === VTable Discovery ===
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
    ComPtr<ID3D11Device> device;
    ComPtr<ID3D11DeviceContext> context;
    ComPtr<IDXGISwapChain> swapchain;

    if (FAILED(D3D11CreateDeviceAndSwapChain(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, 0,
        featureLevels, 1, D3D11_SDK_VERSION, &sd, &swapchain, &device, &featureLevel, &context)))
        return nullptr;

    return *reinterpret_cast<void***>(swapchain.Get());
}

// === Hook Installer ===
void HookPresent()
{
    void** vtable = GetPresentVTable();
    if (!vtable) return;

    void* pPresentAddr = vtable[8];
    void* pResizeBuffersAddr = vtable[13];

    MH_Initialize();
    MH_CreateHook(pPresentAddr, &HookedPresent, reinterpret_cast<void**>(&oPresent));
    MH_EnableHook(pPresentAddr);

    MH_CreateHook(pResizeBuffersAddr, &HookedResizeBuffers, reinterpret_cast<void**>(&oResizeBuffers));
    MH_EnableHook(pResizeBuffersAddr);
}

