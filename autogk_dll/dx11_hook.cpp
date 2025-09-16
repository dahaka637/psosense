// dx11_hook.cpp
#include "menu.hpp"
#include "dx11_hook.hpp"
#include "MinHook/include/MinHook.h"
#include "imgui_style.hpp" 
#include <Windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <iostream>
#include <atomic>
#include "auto_gk.hpp"
#include "imgui.h"
#include "backends/imgui_impl_dx11.h"
#include "backends/imgui_impl_win32.h"

#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "dxgi.lib")

using Microsoft::WRL::ComPtr;

// === Variáveis Globais ===
std::atomic_bool g_ShowWatermark = true;
bool imgui_initialized = false;
bool g_ShowUI = false;

float g_MinCaptureRange = 1.0f;
float g_MaxCaptureRange = 3.0f;

static ID3D11Device* g_pd3dDevice = nullptr;
static ID3D11DeviceContext* g_pd3dDeviceContext = nullptr;
static ID3D11RenderTargetView* g_mainRenderTargetView = nullptr;

static WNDPROC oWndProc = nullptr;
static HWND g_hWnd = nullptr;
static int safe_frame_delay = 0;

typedef HRESULT(APIENTRY* PresentFn)(IDXGISwapChain*, UINT, UINT);
typedef HRESULT(APIENTRY* ResizeBuffersFn)(IDXGISwapChain*, UINT, UINT, UINT, DXGI_FORMAT, UINT);

PresentFn oPresent = nullptr;
ResizeBuffersFn oResizeBuffers = nullptr;

// === WndProc Hook ===
LRESULT CALLBACK WndProcHook(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
    if (g_ShowUI) {
        ImGuiIO& io = ImGui::GetIO();
        // Certifique-se de declarar a função extern se não estiver no escopo
        extern LRESULT ImGui_ImplWin32_WndProcHandler(HWND, UINT, WPARAM, LPARAM);
        if (ImGui_ImplWin32_WndProcHandler(hWnd, uMsg, wParam, lParam)) {
            if (io.WantCaptureMouse || io.WantCaptureKeyboard)
                return true;
        }
    }

    return CallWindowProc(oWndProc, hWnd, uMsg, wParam, lParam);
}


// === Render Target ===
void CreateRenderTarget(IDXGISwapChain* pSwapChain) {
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

HRESULT APIENTRY HookedResizeBuffers(IDXGISwapChain* pSwapChain, UINT BufferCount, UINT Width, UINT Height, DXGI_FORMAT NewFormat, UINT SwapChainFlags) {
    if (g_mainRenderTargetView) g_mainRenderTargetView->Release();
    if (g_pd3dDeviceContext) g_pd3dDeviceContext->OMSetRenderTargets(0, nullptr, nullptr);
    return oResizeBuffers(pSwapChain, BufferCount, Width, Height, NewFormat, SwapChainFlags);
}
HRESULT APIENTRY HookedPresent(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags) {
    if (!imgui_initialized) {
        if (++safe_frame_delay < 60)
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
        io.ConfigFlags |= ImGuiConfigFlags_NoMouseCursorChange;  // evita bugs de cursor duplo


        ApplyCustomImGuiStyle(); // ✅ Estilo PSOSENSE

        ImGui_ImplWin32_Init(g_hWnd);
        oWndProc = (WNDPROC)SetWindowLongPtr(g_hWnd, GWLP_WNDPROC, (LONG_PTR)WndProcHook);
        ImGui_ImplDX11_Init(g_pd3dDevice, g_pd3dDeviceContext);

        CreateRenderTarget(pSwapChain);
        imgui_initialized = true;
    }

    if (!g_mainRenderTargetView)
        CreateRenderTarget(pSwapChain);

    g_pd3dDeviceContext->OMSetRenderTargets(1, &g_mainRenderTargetView, nullptr);

    // Toggle UI com tecla Insert (pressionamento único)
    static bool wasInsertDown = false;
    bool isInsertDown = GetAsyncKeyState(VK_INSERT) & 0x8000;
    if (isInsertDown && !wasInsertDown) {
        g_ShowUI = !g_ShowUI;

        ImGuiIO& io = ImGui::GetIO();
        io.MouseDrawCursor = false;  // não usar cursor manual
        ShowCursor(g_ShowUI);

        if (g_ShowUI) {
            SetCapture(NULL);               // libera foco do mouse
            SetForegroundWindow(g_hWnd);   // força foco na janela do jogo
        }

    }
    wasInsertDown = isInsertDown;

    // Execução do Keybind mesmo com UI oculta
    extern bool g_EnableForceCatchKey;
    extern bool g_WaitingForKey;
    extern int g_ForceCatchKey;
    extern float g_feedbackTimer;
    extern char g_feedbackText[64];

    static ULONGLONG lastKeyPressTime = 0;

    if (g_EnableForceCatchKey && !g_WaitingForKey) {
        if (GetAsyncKeyState(g_ForceCatchKey) & 0x0001) { // Pressionamento único
            ULONGLONG now = GetTickCount64();
            if (now - lastKeyPressTime >= 1000) { // Delay de 1 segundo
                AutoGK::ForceCatchBall();
                snprintf(g_feedbackText, sizeof(g_feedbackText), "Manual Catch (Key)!");
                g_feedbackTimer = 2.5f;
                lastKeyPressTime = now;
            }
        }
    }

    // Frame ImGui
    ImGui_ImplDX11_NewFrame();
    ImGui_ImplWin32_NewFrame();
    ImGui::NewFrame();

    if (g_ShowUI) {
        RenderImGuiInterface();
    }

    ImGui::Render();
    ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

    return oPresent(pSwapChain, SyncInterval, Flags);
}


// === VTable Setup ===
void** GetPresentVTable() {
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

    if (FAILED(D3D11CreateDeviceAndSwapChain(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, 0, featureLevels, 1,
        D3D11_SDK_VERSION, &sd, &swapchain, &device, &featureLevel, &context))) return nullptr;

    return *reinterpret_cast<void***>(swapchain.Get());
}

// === Hook Setup ===
void HookPresent() {
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

// === Utilitários ===
void EnableWatermark() { g_ShowWatermark = true; }
void DisableWatermark() { g_ShowWatermark = false; }
