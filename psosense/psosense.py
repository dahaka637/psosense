import hashlib
import os
import platform
import psutil
import tkinter as tk
import customtkinter
import customtkinter as ctk
from tkinter import messagebox  
from pymem import *
from pymem.process import *
from CTkListbox import *
import threading
import time
from tkinter import *
import verificador_web
from verificador_web import *
import keyboard
import traceback  
from PIL import Image
from miscs import *
import sys
import ctypes
import random
import string
import pyautogui
import itertools
from memory import *
from pipeinject import *
import pipeinject
import error_notify
from error_notify import *

hwid = hashlib.md5(platform.uname().node.encode()).hexdigest()
validation_status = False
chamada_concluida = False
process_name = "ProSoccerOnline-Win64-Shipping.exe"


# Estilo do gui

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")



def verificar_validade():
    global validation_status
    validation_status = verificador_web.situacao_variaveis_seguranca()
    return validation_status


# ENDEREÇOS

gworld = None
enabehcheatvalue = True
staminaAddr = None
staminaAddrCooldown = None
staminaValue = None
speedAddr = None
fovAddr = None
dribblingAddr = None
vagaAddr = None
cameraheightAddr = False
kicktimeAddr = False
handthrowAddr = False
juggleAddr = False
kickPositionAddr = None
KickLeghtAddr = None
GkDriveMomentAddr = None
dribblingPosition = None
dribblingLeght = None

# keys
stamina_key_bind = "<KEY>"
kick_charge_key_bind = "<KEY>"
menu_key_bind = "INSERT"
spawn_ball_key_bind = "Q"

kick_charge_key_has_pressed = False
antikick_interruptor_ativo = False
spawnball_interruptor_ativo = False
kick_charge_ativo = False



def is_process_running():
    process_name = "ProSoccerOnline-Win64-Shipping.exe"
    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'] == process_name:
            return True
    return False




def read_memory(base_address, offsets):
    pm = Pymem('ProSoccerOnline-Win64-Shipping.exe')
    try:
        game_module = module_from_name(pm.process_handle, 'ProSoccerOnline-Win64-Shipping.exe').lpBaseOfDll
        addr = pm.read_longlong(game_module + base_address)
        for offset in offsets:
            if offset != offsets[-1]:
                try:
                    addr = pm.read_longlong(addr + offset)
                except Exception:
                     a = 1
        final_address = addr + offsets[-1]
        return f"0x{final_address:X}"
    except Exception:
        return None

def read_memory_with_fallback():
    """
    Tenta ler os três possíveis endereços de gworld e retorna o primeiro válido.
    """
    possible_gworld_addresses = [
        (0x04629D90, [0x0]),
        (0x041C9A00, [0x0, 0x20, 0x0]),
        (0x04611F80, [0x70, 0x78, 0x0])
    ]

    for base_address, offsets in possible_gworld_addresses:
        gworld = read_memory(base_address, offsets)
        if gworld:
            return gworld  # Retorna o primeiro válido

    raise RuntimeError("Nenhum dos endereços de gworld foi válido.")

def update_memory_addresses():
    global staminaAddrCooldown, speedAddr, fovAddr, dribblingAddr, vagaAddr, cameraheightAddr, kicktimeAddr, handthrowAddr, juggleAddr, kickPositionAddr, KickLeghtAddr, dribblingLeght, dribblingPosition, GkDriveMomentAddr, gworld
    try:
        # Definir o gworld utilizando a função de fallback
        gworld = read_memory_with_fallback()
        
        # Chamar a função montar_estrutura com o gworld válido
        address_data = montar_estrutura(int(gworld, 16))  # Convertendo gworld para int e passando para a função

        # Atribuir os valores retornados para as variáveis globais
        staminaAddrCooldown = address_data.get("staminaAddrCooldown")
        speedAddr = address_data.get("speedAddr")
        fovAddr = address_data.get("fovAddr")
        dribblingAddr = address_data.get("dribblingAddr")
        vagaAddr = address_data.get("vagaAddr")
        cameraheightAddr = address_data.get("cameraheightAddr")
        kicktimeAddr = address_data.get("kicktimeAddr")
        handthrowAddr = address_data.get("handthrowAddr")
        juggleAddr = address_data.get("juggleAddr")
        kickPositionAddr = address_data.get("kickPositionAddr")
        KickLeghtAddr = address_data.get("KickLeghtAddr")
        dribblingLeght = address_data.get("dribblingLeght")
        dribblingPosition = address_data.get("dribblingPosition")
        GkDriveMomentAddr = address_data.get("GkDriveMomentAddr")

    except RuntimeError as e:
        print(f"Erro ao definir os endereços: {str(e)}")







def gerar_titulo_aleatorio(tamanho=21):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

    
def iniciar_software():
    update_memory_addresses()
    pm = Pymem('ProSoccerOnline-Win64-Shipping.exe')

    class App(customtkinter.CTk):
        def __init__(self):
            super().__init__()
            self.protocol("WM_DELETE_WINDOW", self.close_app)

            self.title(gerar_titulo_aleatorio())
            self.overrideredirect(True)
            self.attributes("-alpha", 0.8)
            self.attributes("-topmost", True)
            self.resizable(False, False)

            # Inicializando as variáveis de thread
            self.funcao_geral_thread = None
            self.funcao_handthrow_thread = None
            self.funcao_verificador_thread = None
        

            # Definir ícone da janela
            diretorio_script = os.path.dirname(os.path.abspath(__file__))
            nome_icone = "LOGO.ico"
            caminho_icone = os.path.join(diretorio_script, nome_icone)
            if os.path.exists(caminho_icone):
                self.iconbitmap(caminho_icone)


            # Centralizar a janela
            width, height = 400, 600
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.geometry(f"{width}x{height}+{x}+{y}")


## parada das binds 
            self.teclas_disponiveis = ['w', 'a', 's', 'd', 'shift', 'space', 'ctrl']
            self.hotkey_ids = {
                'stamina': [],
                'kick_charge': [],
                'menu': [],
                'spawn_ball': [],
            }
            self.iniciar_watchdog()
## fin das binds


##teste
            # Inicializar as coordenadas de movimento
            self._offset_x = 0
            self._offset_y = 0

            # Definir uma barra de título customizada para permitir arrastar
            self.title_bar = customtkinter.CTkFrame(self, height=30, fg_color="gray20")
            self.title_bar.pack(side="top", fill="x")

            self.title_label = customtkinter.CTkLabel(self.title_bar, text="PSOSENSE 4.5.3", text_color="white")
            self.title_label.pack(side="left", padx=10)

            # Adicionar os eventos de arrastar à barra de título
            self.title_bar.bind("<Button-1>", self.start_move)
            self.title_bar.bind("<B1-Motion>", self.do_move)

            # Botão de fechar (X) no canto superior direito
            self.close_button = customtkinter.CTkButton(self.title_bar, text="X", width=30, height=10, fg_color="red", hover_color="darkred", text_color="white", command=self.close_app)
            self.close_button.place(relx=1.0, rely=0.0, x=-5, y=5, anchor="ne")

            # Botão de minimizar (-) no canto superior direito, ao lado do botão de fechar
            self.minimize_button = customtkinter.CTkButton(
                self.title_bar, 
                text="-", 
                width=30, 
                height=10, 
                fg_color="gray30", 
                hover_color="lightblue", 
                text_color="white", 
                command=self.minimizar  # Função de minimizar a janela
            )
            self.minimize_button.place(relx=0.999, rely=0.0, x=-45, y=5, anchor="ne")


##teste



            # Criação do TabView
            self.tabview = customtkinter.CTkTabview(self)
            self.tabview.place(relx=0.05, rely=0.03, relwidth=0.9, relheight=0.95)



            # Elevar o botão acima de outros widgets
            self.title_bar.lift()

            # Aba "Functions"
            self.functions_tab = self.tabview.add("Functions")
            self._valorSpeed = customtkinter.IntVar(value=0)
            self._valorFov = customtkinter.DoubleVar(value=80)
            self._valorDribbling = customtkinter.DoubleVar(value=100)
            self._valorCam = customtkinter.IntVar(value=0)
            self._valorKicking = customtkinter.DoubleVar(value=100)
            self._valorhandThrow = customtkinter.DoubleVar(value=0)
            self._valorjuggle = customtkinter.DoubleVar(value=100)
            self._valorGkDriveMoment = customtkinter.DoubleVar(value=0)
            




            # Adicionando um label chamado "marca" com o texto "PSOSENSE" no lado esquerdo da barra de tarefas
            marca = customtkinter.CTkLabel(self.functions_tab, text="PSO", font=("Consolas", 43, "bold"))
            marca.place(relx=0.22, rely=0.05, anchor="w")

            marca2 = customtkinter.CTkLabel(self.functions_tab, text="SENSE", text_color="#2FA572", font=("Consolas", 43, "bold"))
            marca2.place(relx=0.45, rely=0.05, anchor="w")


            # Posições ajustadas para evitar sobreposição de textos e sliders
            espacamento = 0.085
            posicao_base = 0.16
            posicao_speed = posicao_base
            posicao_fov = posicao_base + espacamento * 4
            posicao_dribbling = posicao_base + espacamento * 1
            posicao_kicking = posicao_base + espacamento * 2
            posicao_camheight = posicao_base + espacamento * 5
            posicao_handThrow = posicao_base + espacamento * 6
            posicao_juggle = posicao_base + espacamento * 3
            posicao_gkdrive = posicao_base + espacamento * 7
            posicao_stamina = posicao_base + espacamento * 7.7
            posicao_antikick = posicao_base + espacamento * 8.5
            posicao_touchslow = posicao_base + espacamento * 9.3


            # Sliders na aba "Functions"
            self.slider2 = customtkinter.CTkSlider(self.functions_tab, from_=0, to=150, variable=self._valorSpeed)
            self.slider2.place(relx=0.5, rely=posicao_speed, anchor="center")

            self.slider3 = customtkinter.CTkSlider(self.functions_tab, from_=80, to=175, variable=self._valorFov)
            self.slider3.place(relx=0.5, rely=posicao_fov, anchor="center")

            self.slider4 = customtkinter.CTkSlider(self.functions_tab, from_=0, to=200, variable=self._valorDribbling)
            self.slider4.place(relx=0.5, rely=posicao_dribbling, anchor="center")

            self.slider5 = customtkinter.CTkSlider(self.functions_tab, from_=0, to=200, variable=self._valorKicking)
            self.slider5.place(relx=0.5, rely=posicao_kicking, anchor="center")

            self.slider6 = customtkinter.CTkSlider(self.functions_tab, from_=0, to=150, variable=self._valorCam)
            self.slider6.place(relx=0.5, rely=posicao_camheight, anchor="center")

            self.slider7 = customtkinter.CTkSlider(self.functions_tab, from_=0, to=100, variable=self._valorhandThrow)
            self.slider7.place(relx=0.5, rely=posicao_handThrow, anchor="center")

            self.slider8 = customtkinter.CTkSlider(self.functions_tab, from_=0, to=200, variable=self._valorjuggle)
            self.slider8.place(relx=0.5, rely=posicao_juggle, anchor="center")

            self.slider9 = customtkinter.CTkSlider(self.functions_tab, from_=0, to=100, variable=self._valorGkDriveMoment)
            self.slider9.place(relx=0.5, rely=posicao_gkdrive, anchor="center")

            # Labels de descrição
            self.value_display_labels2 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider2.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels2.place(relx=0.9, rely=posicao_speed, anchor="center")

            self.value_display_labels3 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider3.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels3.place(relx=0.85, rely=posicao_fov, anchor="center")

            self.value_display_labels4 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider4.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels4.place(relx=0.85, rely=(posicao_dribbling), anchor="center")

            self.value_display_labels5 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider5.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels5.place(relx=0.85, rely=posicao_kicking, anchor="center")

            self.value_display_labels6 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider6.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels6.place(relx=0.85, rely=posicao_camheight, anchor="center")

            self.value_display_labels7 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider7.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels7.place(relx=0.85, rely=posicao_handThrow, anchor="center")

            self.value_display_labels8 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider8.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels8.place(relx=0.85, rely=posicao_juggle, anchor="center")

            self.value_display_labels9 = customtkinter.CTkLabel(self.functions_tab, text=str(self.slider9.get()), font=("Consolas", 16, "bold"))
            self.value_display_labels9.place(relx=0.85, rely=posicao_gkdrive, anchor="center")

            # Labels de descrição de função
            self.create_slider_label(self.functions_tab, "Player Speed", posicao_speed - espacamento * 0.5)
            self.create_slider_label(self.functions_tab, "Field of View", posicao_fov - espacamento * 0.5)
            self.create_slider_label(self.functions_tab, "Dribbling Factor", posicao_dribbling - espacamento * 0.5)
            self.create_slider_label(self.functions_tab, "Kicking Factor", posicao_kicking - espacamento * 0.5)
            self.create_slider_label(self.functions_tab, "Camera Height", posicao_camheight - espacamento * 0.5)
            self.create_slider_label(self.functions_tab, "Throw/Kick Force", posicao_handThrow - espacamento * 0.5)
            self.create_slider_label(self.functions_tab, "Juggle Factor", posicao_juggle - espacamento * 0.5)
            self.create_slider_label(self.functions_tab, "GK Jump Distance", posicao_gkdrive - espacamento * 0.5)

            # Interruptor de stamina infinita na aba "Functions"
            self.valorInterruptor = customtkinter.BooleanVar(value=False)

            self.valorAntiKick = customtkinter.BooleanVar(value=False)

            # Interruptor de stamina infinita
            self.valorStamina = customtkinter.BooleanVar(value=False)
            customtkinter.CTkSwitch(
                self.functions_tab,
                variable=self.valorStamina,
                text="Infinite Stamina",
                font=("default", 16, "bold"),
                width=70,
                height=50
            ).place(relx=0.5, rely=posicao_stamina, anchor="center")

            # Interruptor de anti-kick/ban
            self.valorAntiKick = customtkinter.BooleanVar(value=False)

            customtkinter.CTkSwitch(
                self.functions_tab,
                variable=self.valorAntiKick,
                text="Anti-Kick/Ban",
                font=("default", 16, "bold"),
                width=70,
                height=50,
                command=self.toggle_antikick  # <-- Aqui vinculamos a função
            ).place(relx=0.5, rely=posicao_antikick, anchor="center")

            # Interruptor de Touch Slow
            self.valorTouchSlow = customtkinter.BooleanVar(value=False)

            customtkinter.CTkSwitch(
                self.functions_tab,
                variable=self.valorTouchSlow,
                text="Disable Touch Slow",
                font=("default", 16, "bold"),
                width=70,
                height=50,
                command=self.toggle_touchslow  # <-- Função a ser chamada ao alternar
            ).place(relx=0.5, rely=posicao_touchslow, anchor="center")

            
            # Chamada da função de atualização dos valores dos sliders
            self.update_slider_values()

            self.iniciar_todas_as_Threads()

            ########################
            # CONFIG E KEYBIND TAB INICIO
            #######################

            # Aba "Configurações"
            self.Profile_tab = self.tabview.add("Profiles")

            self.keybinds_tab = self.tabview.add("Keybinds")

            # Adicionando um label chamado "marca" com o texto "PSOSENSE" no lado esquerdo da barra de tarefas
            marca5 = customtkinter.CTkLabel(self.keybinds_tab, text="PSO", font=("Consolas", 43, "bold"))
            marca5.place(relx=0.22, rely=0.05, anchor="w")

            marca6 = customtkinter.CTkLabel(self.keybinds_tab, text="SENSE", text_color="#2FA572", font=("Consolas", 43, "bold"))
            marca6.place(relx=0.45, rely=0.05, anchor="w")


            self.valorInterruptor_stamina_key = customtkinter.BooleanVar(value=False)
            switch0 = customtkinter.CTkSwitch(self.keybinds_tab, variable=self.valorInterruptor_stamina_key, text="Stamina refil on KEY press", font=("Consolas", 18, "bold"),
                                            switch_width=40, switch_height=20, corner_radius=20)
            switch0.place(relx=0.5, rely=0.135, anchor="center")  # Centralizado horizontalmente, mais para cima

            # Botão para definir a tecla de stamina
            self.botao_key_stamina = customtkinter.CTkButton(
                self.keybinds_tab,
                text=stamina_key_bind,  # Texto do botão exibindo a tecla atual
                font=("Consolas", 18, "bold"),
                command=lambda: self.definir_tecla('stamina', self.botao_key_stamina),
                hover_color="#5da686",
                fg_color="transparent",
                border_color="#2FA572",
                border_width=1.0
            )
            self.botao_key_stamina.place(relx=0.5, rely=0.23, relwidth=0.20, relheight=0.08, anchor="center")


            # Botão para definir a tecla de full kick charge
            self.botao_key_kick_charge = customtkinter.CTkButton(
                self.keybinds_tab,
                text=kick_charge_key_bind,  # Texto do botão exibindo a tecla atual
                font=("Consolas", 18, "bold"),
                command=lambda: self.definir_tecla('kick_charge', self.botao_key_kick_charge),
                hover_color="#5da686",
                fg_color="transparent",
                border_color="#2FA572",
                border_width=1.0
            )
            self.botao_key_kick_charge.place(relx=0.5, rely=0.43, relwidth=0.20, relheight=0.08, anchor="center")


            # Novo switch para "Full kick charge on key press"
            self.valorInterruptor_kick_charge_key = customtkinter.BooleanVar(value=False)
            switch1 = customtkinter.CTkSwitch(self.keybinds_tab, variable=self.valorInterruptor_kick_charge_key, text="Super Kick on KEY press", font=("Consolas", 18, "bold"),
                                            switch_width=40, switch_height=20, corner_radius=20)
            switch1.place(relx=0.5, rely=0.33, anchor="center")



            # === Botão e switch para "Spawn Ball Bypass" ===

            # Interruptor que ativa/desativa a função ao pressionar a tecla
            self.valorInterruptor_spawn_ball = customtkinter.BooleanVar(value=False)
            switch2 = customtkinter.CTkSwitch(
                self.keybinds_tab,
                variable=self.valorInterruptor_spawn_ball,
                text="Spawn Ball on KEY press",
                font=("Consolas", 18, "bold"),
                switch_width=40,
                switch_height=20,
                corner_radius=20
            )
            switch2.place(relx=0.5, rely=0.52, anchor="center")  # Ajuste vertical abaixo do anterior

            # Botão para definir a tecla de ativação do spawn ball bypass
            self.botao_key_spawn_ball = customtkinter.CTkButton(
                self.keybinds_tab,
                text=spawn_ball_key_bind,  # Você deve definir essa variável antes, como fez com as outras
                font=("Consolas", 18, "bold"),
                command=lambda: self.definir_tecla('spawn_ball', self.botao_key_spawn_ball),
                hover_color="#5da686",
                fg_color="transparent",
                border_color="#2FA572",
                border_width=1.0
            )
            self.botao_key_spawn_ball.place(relx=0.5, rely=0.62, relwidth=0.20, relheight=0.08, anchor="center")







            # Adicionando o Label e o botão na interface para definir o bind da tecla do menu
            descricao_key_binder = customtkinter.CTkLabel(self.keybinds_tab, text="Bind key to open/hide menu", font=("Consolas", 20, "bold"))
            descricao_key_binder.place(relx=0.5, rely=0.72, anchor="center")

            # Certifique-se de que este código esteja dentro do __init__ ou em um método chamado antes de tentar configurar o botão
            self.botao_definir_tecla = customtkinter.CTkButton(
                self.keybinds_tab, 
                text=menu_key_bind, 
                font=("Consolas", 18, "bold"), 
                command=lambda: self.definir_tecla('menu', self.botao_definir_tecla),
                hover_color="#5da686", 
                fg_color="transparent", 
                border_color="#2FA572", 
                border_width=1.0
            )
            self.botao_definir_tecla.place(relx=0.5, rely=0.82, relwidth=0.25, relheight=0.08, anchor="center")

                                    
            # Variável de controle
            self.valorCheckbox_watermark = customtkinter.BooleanVar(value=True)

            # Checkbox com estilo maior e vinculado à função
            self.checkbox_watermark = customtkinter.CTkCheckBox(
                self.keybinds_tab,
                text="Enable Watermark",
                font=("Consolas", 20, "bold"),
                variable=self.valorCheckbox_watermark,
                onvalue=True,
                offvalue=False,
                command=self.aplicar_configuracao_watermark
            )
            self.checkbox_watermark.place(relx=0.5, rely=0.95, anchor="center")




            # Adicionando um label chamado "marca" com o texto "PSOSENSE" no lado esquerdo da barra de tarefas
            marca3 = customtkinter.CTkLabel(self.Profile_tab, text="PSO", font=("Consolas", 43, "bold"))
            marca3.place(relx=0.22, rely=0.05, anchor="w")

            marca4 = customtkinter.CTkLabel(self.Profile_tab, text="SENSE", text_color="#2FA572", font=("Consolas", 43, "bold"))
            marca4.place(relx=0.45, rely=0.05, anchor="w")

            # Lista de configurações
            self.listbox = CTkListbox(self.Profile_tab)
            self.listbox.place(relx=0.5, rely=0.35, anchor="center", relwidth=0.8, relheight=0.4)
            self.listbox.bind("<<ListboxSelect>>", self.atualizar_entrada_com_selecionado)

            self.configuracao_selecionada = None


            # Campo de entrada para nome da configuração
            self.entry = customtkinter.CTkEntry(self.Profile_tab, placeholder_text="Config Name")
            self.entry.place(relx=0.5, rely=0.65, relwidth=0.8, relheight=0.1, anchor="center")


            # Diretório para ícones
            diretorio_imagens = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

            # Ícone para carregar configuração
            iconeUpload = customtkinter.CTkImage(Image.open(os.path.join(diretorio_imagens, "upload.png")), size=(25, 25))
            self.iconeUpload = customtkinter.CTkLabel(self.Profile_tab, text="Load", text_color="#9ab9ff", image=iconeUpload, compound="top", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.iconeUpload.place(relx=0.2, rely=0.8, anchor="center")
            self.iconeUpload.bind("<Button-1>", self.on_upload_click)

            # Ícone para deletar configuração
            iconeDelete = customtkinter.CTkImage(Image.open(os.path.join(diretorio_imagens, "trash.png")), size=(25, 25))
            self.iconeDelete = customtkinter.CTkLabel(self.Profile_tab, text="Delete", text_color="#ff8282", image=iconeDelete, compound="top", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.iconeDelete.place(relx=0.5, rely=0.8, anchor="center")
            self.iconeDelete.bind("<Button-1>", self.on_delete_click)

            # Ícone para salvar configuração
            iconeSave = customtkinter.CTkImage(Image.open(os.path.join(diretorio_imagens, "save.png")), size=(25, 25))
            self.iconeSave = customtkinter.CTkLabel(self.Profile_tab, text="Save", text_color="#d4ff9a", image=iconeSave, compound="top", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.iconeSave.place(relx=0.8, rely=0.8, anchor="center")
            self.iconeSave.bind("<Button-1>", self.on_save_click)
            
            # Label de feedback visual
            self.feedback_label = customtkinter.CTkLabel(self.Profile_tab, text="", font=("Consolas", 16, "bold"))
            self.feedback_label.place(relx=0.5, rely=0.92, anchor="center")

            self.carregar_configuracoes_existentes()
            self.fazer_hook_tecla()


            self.lobby_tab = self.tabview.add("Lobby")

            # Adicionando um label chamado "marca" com o texto "PSOSENSE" no lado esquerdo da barra de tarefas
            marca5 = customtkinter.CTkLabel(self.lobby_tab, text="PSO", font=("Consolas", 43, "bold"))
            marca5.place(relx=0.22, rely=0.05, anchor="w")

            marca6 = customtkinter.CTkLabel(self.lobby_tab, text="SENSE", text_color="#2FA572", font=("Consolas", 43, "bold"))
            marca6.place(relx=0.45, rely=0.05, anchor="w")

            # === Ícones (mantenha isso onde você já carrega os ícones) ===
            # === Caminho absoluto da pasta onde o script está ===
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            IMG_DIR = os.path.join(BASE_DIR, "img")

            # === Ícones (com caminho absoluto) ===
            icon_swap = customtkinter.CTkImage(Image.open(os.path.join(IMG_DIR, "swap.png")), size=(30, 30))
            icon_keeper = customtkinter.CTkImage(Image.open(os.path.join(IMG_DIR, "keeper.png")), size=(30, 30))
            icon_start = customtkinter.CTkImage(Image.open(os.path.join(IMG_DIR, "start.png")), size=(30, 30))
            icon_slot = customtkinter.CTkImage(Image.open(os.path.join(IMG_DIR, "slot.png")), size=(30, 30))

            # === Botões verticais no Lobby ===
            botao_altura = 45
            espacamento = 0.12
            inicio_y = 0.25

            customtkinter.CTkButton(
                self.lobby_tab,
                text=" Force Swap",
                image=icon_swap,
                compound="left",
                font=("default", 16, "bold"),
                height=botao_altura,
                corner_radius=10,
                command=lambda: pipeinject.force_swap()
            ).place(relx=0.5, rely=inicio_y, relwidth=0.8, anchor="center")

            customtkinter.CTkButton(
                self.lobby_tab,
                text=" Toggle Single Keeper",
                image=icon_keeper,
                compound="left",
                font=("default", 16, "bold"),
                height=botao_altura,
                corner_radius=10,
                command=lambda: pipeinject.toggle_keeper()
            ).place(relx=0.5, rely=inicio_y + espacamento, relwidth=0.8, anchor="center")

            customtkinter.CTkButton(
                self.lobby_tab,
                text=" Start/Restart Match",
                image=icon_start,
                compound="left",
                font=("default", 16, "bold"),
                height=botao_altura,
                corner_radius=10,
                command=lambda: pipeinject.reset_match()
            ).place(relx=0.5, rely=inicio_y + espacamento * 2, relwidth=0.8, anchor="center")

            customtkinter.CTkButton(
                self.lobby_tab,
                text=" Add Slot",
                image=icon_slot,
                compound="left",
                font=("default", 16, "bold"),
                height=botao_altura,
                corner_radius=10,
                command=self.add_slot
            ).place(relx=0.5, rely=inicio_y + espacamento * 3, relwidth=0.8, anchor="center")


        # FUNÇÕES DO CONFIG

        def exibir_feedback(self, mensagem, cor):
            # Definir a largura máxima do label para a quebra de linha automática
            wrap_length = 350  # Ajuste o valor conforme a largura desejada

            # Atualizar o texto, a cor do feedback e definir o wraplength
            self.feedback_label.configure(text=mensagem, text_color=cor, wraplength=wrap_length)

            # Função para limpar o feedback após 5 segundos
            def limpar_feedback():
                self.feedback_label.configure(text="")
            
            # Limpar o feedback após 5 segundos
            self.after(5000, limpar_feedback)


            # Ícone upload
        def on_upload_click(self, event):
            print("Clicou no ícone de carregar!")
            self.carregar_configuracao()
            self.iconeUpload.configure(text_color="#00ccff", font=customtkinter.CTkFont(size=18, weight="bold"))
            def restore_icon():
                self.iconeUpload.configure(text_color="#9ab9ff", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.after(100, restore_icon)


            # Ícone save
        def on_save_click(self, event):
                print("Clicou no ícone de salvar!")
                self.salvar_valores_config()
                self.iconeSave.configure(text_color="#00ff1d", font=customtkinter.CTkFont(size=18, weight="bold"))
                def restore_icon():
                    self.iconeSave.configure(text_color="#d4ff9a", font=customtkinter.CTkFont(size=20, weight="bold"))
                app.after(100, restore_icon)

            # Ícone delete
        def on_delete_click(self, event):
            print("Clicou no ícone de deletar!")
            self.deletar_configuracao()
            self.iconeDelete.configure(text_color="#ff0000", font=customtkinter.CTkFont(size=18, weight="bold"))
            def restore_icon():
                self.iconeDelete.configure(text_color="#ff8282", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.after(100, restore_icon)


        # Diretório para os arquivos de configuração
        diretorio_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")


        # No App dentro do seu main.py

        def salvar_valores_config(self):
            global stamina_key_bind, kick_charge_key_bind, menu_key_bind, spawn_ball_key_bind  # Declarar como global
            nome = self.entry.get().strip()  # Pega o nome da configuração da entrada do usuário
            if not nome:
                self.exibir_feedback("The configuration name cannot be empty!", "#ff0000")  
                return

            # Pegue os valores das variáveis
            valorDribbling = self._valorDribbling.get()
            valorKicking = self._valorKicking.get()
            valorSpeed = self._valorSpeed.get()
            interruptorStamina = self.valorInterruptor.get()
            interruptorStamina_Key = self.valorInterruptor_stamina_key.get() 
            staminakeybind = stamina_key_bind 
            interruptorkickchargekey = self.valorInterruptor_kick_charge_key.get()
            # Novos interruptores e tecla
            interruptorSpawnBall = self.valorInterruptor_spawn_ball.get()
            spawnballkeybind = spawn_ball_key_bind
            interruptorAntiKick = self.valorAntiKick.get()
            kickchargekeybind = kick_charge_key_bind
            menukeybind = menu_key_bind
            valorFov = self._valorFov.get()
            valorCameraHeight = self._valorCam.get()
            valorHandTrow = self._valorhandThrow.get()
            valor_juggle = self._valorjuggle.get()
            valor_GkDrive = self._valorGkDriveMoment.get()
            valor_infinite_stamina = self.valorStamina.get()
            watermark = self.valorCheckbox_watermark.get()
            TouchSlow = self.valorTouchSlow.get()


            # Chame a função que salva no JSON
            salvar_configuracao(
                nome,
                valorDribbling,
                valorKicking,
                valorSpeed,
                interruptorStamina,
                interruptorStamina_Key,
                interruptorkickchargekey,
                kickchargekeybind,
                staminakeybind, 
                menukeybind,
                valorFov,
                valorCameraHeight,
                valorHandTrow,
                valor_juggle,
                valor_GkDrive,
                interruptorSpawnBall,
                spawnballkeybind,
                interruptorAntiKick,
                valor_infinite_stamina,
                watermark,
                TouchSlow
            )
            self.exibir_feedback("Configuration saved successfully!", "#00ff1d")  
            self.entry.delete(0, "end")  # Limpe o campo de entrada após salvar
            self.carregar_configuracoes_existentes()


        def carregar_configuracoes_existentes(self):
            try:
                # Diretório onde as configurações estão salvas
                diretorio_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")

                # Limpar a listbox antes de preencher novamente
                self.listbox.delete(0, 'end')

                # Verificar se o diretório de configurações existe
                if os.path.exists(diretorio_config):
                    print(f"Verificando configurações no diretório: {diretorio_config}")
                    # Listar todos os arquivos .json no diretório de configurações
                    arquivos_encontrados = []
                    for arquivo in os.listdir(diretorio_config):
                        if arquivo.endswith(".json"):
                            # Adicionar o nome do arquivo (sem extensão .json) à listbox
                            nome_configuracao = os.path.splitext(arquivo)[0]
                            arquivos_encontrados.append(nome_configuracao)
                            self.listbox.insert('end', nome_configuracao)
                            print(f"Configuração encontrada: {nome_configuracao}")
                    
                    if not arquivos_encontrados:
                        print("Nenhuma configuração .json encontrada no diretório.")
                else:
                    print(f"Diretório '{diretorio_config}' não encontrado.")

            except Exception as e:
                print(f"Erro ao carregar as configurações: {str(e)}")


        def deletar_configuracao(self):
            # Imprimir todos os itens da listbox e seus índices
            print("Configurações na lista:")
            for index in range(self.listbox.size()):
                nome_configuracao = self.listbox.get(index)
                print(f"Index {index}: {nome_configuracao}")

            # Verificar se há alguma configuração selecionada
            if self.configuracao_selecionada:
                nome_configuracao = self.configuracao_selecionada

                print(f"Configuração selecionada para exclusão: {nome_configuracao}")

                # Caminho completo do arquivo de configuração a ser deletado
                caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", f"{nome_configuracao}.json")

                # Verificar se o arquivo existe e deletá-lo
                if os.path.exists(caminho_arquivo):
                    try:
                        os.remove(caminho_arquivo)
                        print(f"Configuração '{nome_configuracao}' deletada com sucesso.")
                        self.exibir_feedback(f"Config '{nome_configuracao}' successfully deleted!", "#00ff1d")

                        # Recarregar a lista de configurações após a exclusão
                        self.carregar_configuracoes_existentes()
                    except Exception as e:
                        print(f"Erro ao deletar a configuração: {str(e)}")
                        self.exibir_feedback(f"Error when deleting configuration: {str(e)}", "#ff0000")
                else:
                    self.exibir_feedback("Configuration file not found.", "#ff0000")
            else:
                print("Nenhuma configuração selecionada.")
                self.exibir_feedback("No settings selected.", "#ff0000")


        def carregar_configuracao(self):
            if not self.configuracao_selecionada:
                self.exibir_feedback("No config selected.", "#ff0000")
                print("Nenhuma configuração selecionada para carregar.")
                return

            print(f"Carregando a configuração: {self.configuracao_selecionada}")
            configuracao = carregar_configuracao(self.configuracao_selecionada)

            if not configuracao:
                self.exibir_feedback("Failed to load config.", "#ff0000")
                print(f"Erro ao carregar a configuração '{self.configuracao_selecionada}'.")
                return

            print(f"Configuração '{self.configuracao_selecionada}' carregada com sucesso.")

            # === Sliders / Valores numéricos ===
            self._valorDribbling.set(configuracao.get("valorDribbling", 100.0))
            self._valorKicking.set(configuracao.get("valorKicking", 100.0))
            self._valorSpeed.set(configuracao.get("valorSpeed", 0))
            self._valorFov.set(configuracao.get("valorFov", 80.0))
            self._valorCam.set(configuracao.get("valorCameraHeight", 0))
            self._valorhandThrow.set(configuracao.get("valorHandTrow", 0))
            self._valorjuggle.set(configuracao.get("valorjuggle", 100.0))
            self._valorGkDriveMoment.set(configuracao.get("valor_GkDrive", 0))

            # === Interruptores (switches booleanos) ===
            self.valorInterruptor.set(bool(configuracao.get("interruptorStamina", False)))
            self.valorInterruptor_stamina_key.set(bool(configuracao.get("interruptorStamina_Key", False)))
            self.valorInterruptor_kick_charge_key.set(bool(configuracao.get("interruptorkickchargekey", False)))
            self.valorInterruptor_spawn_ball.set(bool(configuracao.get("interruptorSpawnBall", False)))
            self.valorAntiKick.set(bool(configuracao.get("interruptorAntiKick", False)))
            self.valorStamina.set(bool(configuracao.get("valorInfiniteStamina", False)))
            self.valorCheckbox_watermark.set(bool(configuracao.get("watermark", True)))
            self.valorTouchSlow.set(bool(configuracao.get("TouchSlow", False)))

            # === Teclas (binds globais e botões visuais) ===
            global stamina_key_bind, kick_charge_key_bind, menu_key_bind, spawn_ball_key_bind
            stamina_key_bind = configuracao.get("staminakeybind", "<KEY>")
            kick_charge_key_bind = configuracao.get("kickchargekeybind", "<KEY>")
            menu_key_bind = configuracao.get("menukeybind", "<KEY>")
            spawn_ball_key_bind = configuracao.get("spawnballkeybind", "<KEY>")

            self.botao_key_stamina.configure(text=stamina_key_bind)
            self.botao_key_kick_charge.configure(text=kick_charge_key_bind)
            self.botao_definir_tecla.configure(text=menu_key_bind)
            self.botao_key_spawn_ball.configure(text=spawn_ball_key_bind)

            # === Feedback e ações finais ===
            self.exibir_feedback(f"Config '{self.configuracao_selecionada}' loaded successfully!", "#00ff1d")
            self.toggle_antikick()
            self.aplicar_configuracao_watermark()
            self.toggle_touchslow()
            self.fazer_hook_tecla()



        # Função para armazenar o arquivo selecionado
        def atualizar_entrada_com_selecionado(self, event):
            # Verificar qual item está selecionado
            selecionado = self.listbox.curselection()
            print(f"Selecionado: {selecionado}")

            # Verificar se selecionado é um número inteiro válido
            if isinstance(selecionado, int) and selecionado >= 0:
                index_selecionado = selecionado  # Pega o índice selecionado
                self.configuracao_selecionada = self.listbox.get(index_selecionado)
                print(f"Configuração selecionada: {self.configuracao_selecionada}")
                self.entry.delete(0, 'end')  # Limpa o campo de entrada
                self.entry.insert(0, self.configuracao_selecionada)
            else:
                # Caso não haja seleção válida
                self.configuracao_selecionada = None
                print("Nenhuma configuração selecionada.")



            #####################
            # parte das binds



            # Lista de teclas disponíveis para combinações
            
         
        def iniciar_watchdog(self):
            threading.Thread(target=self._verificar_binds, daemon=True).start()

        def _verificar_binds(self):
            time.sleep(5)
            while True:
                for tipo, tecla in {
                    'stamina': stamina_key_bind,
                    'kick_charge': kick_charge_key_bind,
                    'menu': menu_key_bind,
                    'spawn_ball': spawn_ball_key_bind,
                }.items():
                    if tecla == "<KEY>":
                        continue

                    if not self.hotkey_ids.get(tipo):
                        print(f"[Watchdog] Reconfigurando bind perdida: {tipo}")
                        self.fazer_hook_tecla()
                        break

                time.sleep(10)

        def fazer_hook_tecla(self):
            global stamina_key_bind, kick_charge_key_bind, menu_key_bind, spawn_ball_key_bind
            keyboard.unhook_all()
            print("[INFO] Reconfigurando hotkeys...")
            self._definir_bind('stamina', stamina_key_bind, self.funcao_stamina_refil)
            self._definir_bind('kick_charge', kick_charge_key_bind, self.funcao_full_kick_charge)
            self._definir_bind('menu', menu_key_bind, self.toggle_minimize_maximize)
            self._definir_bind('spawn_ball', spawn_ball_key_bind, self.funcao_spawn_ball_bypass)

        def _definir_bind(self, tipo, key_bind, funcao, max_comb=4):
            self._remover_binds(tipo)
            if key_bind != "<KEY>":
                hotkeys = []
                hotkeys.append(keyboard.add_hotkey(key_bind, funcao))
                for comb_length in range(1, max_comb + 1):
                    for comb in itertools.combinations(self.teclas_disponiveis, comb_length):
                        if key_bind in comb:
                            continue
                        comb_str = '+'.join(comb) + f'+{key_bind}'
                        if len(set(comb)) == len(comb):
                            hotkeys.append(keyboard.add_hotkey(comb_str, funcao))
                self.hotkey_ids[tipo] = hotkeys

        def _remover_binds(self, tipo):
            for hotkey_id in self.hotkey_ids[tipo]:
                try:
                    keyboard.remove_hotkey(hotkey_id)
                except:
                    pass
            self.hotkey_ids[tipo] = []

        def capturar_tecla_generico(self, event, tipo, botao):
            global stamina_key_bind, kick_charge_key_bind, menu_key_bind, spawn_ball_key_bind
            tecla = event.name.upper() if hasattr(event, 'name') else str(event).upper()
            botao.configure(text=tecla)

            if tipo == 'stamina':
                stamina_key_bind = tecla
            elif tipo == 'kick_charge':
                kick_charge_key_bind = tecla
            elif tipo == 'menu':
                menu_key_bind = tecla
            elif tipo == 'spawn_ball':
                spawn_ball_key_bind = tecla

            keyboard.unhook_all()
            self.fazer_hook_tecla()

        def definir_tecla(self, tipo, botao):
            keyboard.unhook_all()
            keyboard.on_press(lambda e: self.capturar_tecla_generico(e, tipo, botao))
            botao.configure(text="...")

        # === Funções associadas aos binds ===

        def funcao_stamina_refil(self):
            if self.valorInterruptor_stamina_key.get():
                print("⚡ Recarregando stamina...")
                self.executar_stamina_refil()

        def funcao_full_kick_charge(self):
            if self.valorInterruptor_kick_charge_key.get():
                print("⚽ Full Kick Charge ativado")
                self.kick_charge()

        def funcao_spawn_ball_bypass(self):
            if self.valorInterruptor_spawn_ball.get():
                print("🟢 Spawn Ball bypass ativado")
                pipeinject.spawn_ball()

        def toggle_minimize_maximize(self):
            if self.winfo_viewable():
                self.withdraw()
            else:
                self.deiconify()
                self.lift()
                self.focus_force()
                x = self.winfo_rootx() + self.winfo_width() // 2
                y = self.winfo_rooty() + self.winfo_height() // 5
                pyautogui.moveTo(x, y)
                pyautogui.click()


            ########################
            # CONFIG E KEYBIND TAB FIM
            #######################





        # Função auxiliar para criar labels
        def create_slider_label(self, parent, text, rel_y):
            label = customtkinter.CTkLabel(parent, text=text, font=("Consolas", 17, "bold"))
            label.place(relx=0.5, rely=rel_y, anchor="center")

        # Função para atualizar os valores dos sliders dinamicamente
        def update_slider_values(self):


            #speed
            valor_speed = self.slider2.get()
            if valor_speed == 0:
                self.value_display_labels2.configure(text="Default")
                self.value_display_labels2.place(relx=0.88)
            else:
                self.value_display_labels2.configure(text=f"+{int(valor_speed)}%")
                self.value_display_labels2.place(relx=0.86)
            #fov
            valor_fov = self.slider3.get()
            if valor_fov == 80:
                self.value_display_labels3.configure(text="Default")
                self.value_display_labels3.place(relx=0.88)
            else:
                self.value_display_labels3.configure(text=str(int(valor_fov)))
                self.value_display_labels3.place(relx=0.86)
            # dribbling
            valor_dribbling = self.slider4.get()
            if valor_dribbling == 200:
                self.value_display_labels4.configure(text="Max", text_color="red")
                self.value_display_labels4.place(relx=0.85)
            elif valor_dribbling == 100:
                self.value_display_labels4.configure(text="Default", text_color="white")
                self.value_display_labels4.place(relx=0.88)
            elif valor_dribbling == 0:
                self.slider4.set(100)
            else:
                self.value_display_labels4.configure(text=f"{int(valor_dribbling)}%", text_color="white")
                self.value_display_labels4.place(relx=0.86)
            #kicking
            valor_kicking = self.slider5.get()
            if valor_kicking == 200:
                self.value_display_labels5.configure(text="Max", text_color="red")
                self.value_display_labels5.place(relx=0.85)
            elif valor_kicking == 100:
                self.value_display_labels5.configure(text="Default", text_color="white")
                self.value_display_labels5.place(relx=0.88)
            elif valor_kicking == 0:
                self.slider5.set(100)
            else:
                self.value_display_labels5.configure(text=f"{int(valor_kicking)}%", text_color="white")
                self.value_display_labels5.place(relx=0.86)
            # cam height
            valor_camheight = self.slider6.get()
            if valor_camheight == 0:
                self.value_display_labels6.configure(text="Default")
                self.value_display_labels6.place(relx=0.88)
            else:
                self.value_display_labels6.configure(text=f"+{str(int(valor_camheight))}%")
                self.value_display_labels6.place(relx=0.86)
            # Juggle
            valor_juggle = self.slider8.get()
            if valor_juggle == 200:
                self.value_display_labels8.configure(text="Max", text_color="red")
                self.value_display_labels8.place(relx=0.85)
            elif valor_juggle == 100:
                self.value_display_labels8.configure(text="Default", text_color="white")
                self.value_display_labels8.place(relx=0.88)
            elif valor_juggle == 0:
                self.slider8.set(100)
            else:
                self.value_display_labels8.configure(text=f"{int(valor_juggle)}%", text_color="white")
                self.value_display_labels8.place(relx=0.86)
            valorHandThrow = self.slider7.get()

            if valorHandThrow >= 100:
                self.value_display_labels7.configure(text="Max", text_color="red")
                self.value_display_labels7.place(relx=0.85)

            elif 11 <= valorHandThrow < 100:
                self.value_display_labels7.configure(text=f"+{int(valorHandThrow)}%", text_color="yellow")
                self.value_display_labels7.place(relx=0.86)

            elif 1 <= valorHandThrow < 11:
                self.value_display_labels7.configure(text=f"+{int(valorHandThrow)}%", text_color="#90EE90")
                self.value_display_labels7.place(relx=0.86)

            else:
                self.value_display_labels7.configure(text="Default", text_color="white")
                self.value_display_labels7.place(relx=0.88)


            valor_gkdrive = self.slider9.get()
            if valor_gkdrive == 0:
                self.value_display_labels9.configure(text="Default", text_color="white")
                self.value_display_labels9.place(relx=0.88)
            else:
                self.value_display_labels9.configure(text=f"+{str(int(valor_gkdrive))}%")
                self.value_display_labels9.place(relx=0.86)     

            # Chamada recursiva para atualizar continuamente
            self.after(50, self.update_slider_values)




        def close_app(self):
            os._exit(0)
            
        def iniciar_todas_as_Threads(self):
            self.start_funcao_geral_thread()
            self.start_funcao_handthrow_thread()
            self.start_funcao_verificador_thread()

            
##############
# FUNCTIONS DO CONFIG

                    

# //////////////////////////////////////////////////////
# //////////////== AS FUNÇÕES SERÃO AQUI ==////////////
# ////////////////////////////////////////////////////

        
##################### SPEED



        def manage_game_values(self):
            # Definindo a variável de loop para controle de frequência
            loop_interval = 5.0  # Inicia com 5 segundos por padrão

            while True:
                # Inicializa os estados como True para monitorar o sucesso de cada operação
                status_checks = {
                    "speed_ok": True,
                    "fov_ok": True,
                    "camera_height_ok": True,
                    "dribbling_ok": True,
                    "stamina_ok": True,
                    "gkdrive_ok": True
                }

                try:
                    ### SPEED ###
                    try:
                        if speedAddr:
                            speed_value = round(1.0 + (self._valorSpeed.get() / 115) * 0.25, 2)
                            current_speed_value = pm.read_float(int(speedAddr, 16))
                            if current_speed_value != speed_value:
                                pm.write_float(int(speedAddr, 16), speed_value)
                        else:
                            status_checks["speed_ok"] = False
                    except Exception:
                        status_checks["speed_ok"] = False

                    ### FOV ###
                    try:
                        if fovAddr:
                            fov_value = float(self._valorFov.get())
                            current_fov_value = pm.read_float(int(fovAddr, 16))
                            if current_fov_value != fov_value and fov_value != 80:
                                pm.write_float(int(fovAddr, 16), fov_value)
                        else:
                            status_checks["fov_ok"] = False
                    except Exception:
                        print("Há algum problema com o FOV")
                        status_checks["fov_ok"] = False

                    ### CAMERA HEIGHT ###
                    try:
                        if cameraheightAddr:
                            current_cameraheight_value = pm.read_float(int(cameraheightAddr, 16))
                            cameraheight_value = float(max(self._valorCam.get() * 2.25 + 300, 300))
                            if current_cameraheight_value != cameraheight_value:
                                pm.write_float(int(cameraheightAddr, 16), cameraheight_value)
                        else:
                            status_checks["camera_height_ok"] = False
                    except Exception:
                        print("Há algum problema com o Camera Height")
                        status_checks["camera_height_ok"] = False

                    ### DRIBBLING ###
                    try:
                        if dribblingAddr and kicktimeAddr and juggleAddr:
                            dribbling_value = float(self._valorDribbling.get()) / 100
                            current_dribbling_value = pm.read_float(int(dribblingAddr, 16))

                            juggle_value = float(self._valorjuggle.get()) / 100
                            current_juggle_value = pm.read_float(int(juggleAddr, 16))

                            kicking_value = float(self._valorKicking.get()) / 100
                            current_kicking_value = pm.read_float(int(kicktimeAddr, 16))

                            if current_juggle_value != juggle_value:
                                if juggle_value == 2:
                                    pm.write_float(int(juggleAddr, 16), 99.0)
                                else:
                                    pm.write_float(int(juggleAddr, 16), juggle_value)

                            if current_dribbling_value != dribbling_value:
                                if dribbling_value == 2.0:
                                    pm.write_float(int(dribblingAddr, 16), 30.0)
                                    pm.write_float(int(dribblingPosition, 16), 1.0)
                                else:
                                    pm.write_float(int(dribblingAddr, 16), dribbling_value)

                            if current_kicking_value != kicking_value:
                                if kicking_value == 2.0:
                                    pm.write_float(int(kicktimeAddr, 16), 30.0)
                                    pm.write_float(int(kickPositionAddr, 16), 1.0)
                                else:
                                    pm.write_float(int(kicktimeAddr, 16), kicking_value)
                                
                        else:
                            status_checks["dribbling_ok"] = False
                    except Exception:
                        print("Há algum problema com o Dribbling ou Kicking")
                        status_checks["dribbling_ok"] = False


                    ### STAMINA ###
                    try:
                        if staminaAddrCooldown:
                            if self.valorStamina.get():  # Corrigido o nome da variável
                                endereco = int(staminaAddrCooldown, 16)
                                pm.write_float(endereco, 1.0)
                            # Se o interruptor estiver desligado, não faz nada
                        else:
                            status_checks["stamina_ok"] = False
                    except Exception:
                        status_checks["stamina_ok"] = False

                    
                    #### GK DRIVE ###
                    try:
                        if GkDriveMomentAddr:
                            # Calculando o valor esperado e arredondando para 3 casas decimais
                            GkDrive_Value = round(0.300 + (self._valorGkDriveMoment.get()) / 165, 3)
                            
                            # Lendo o valor atual da memória e arredondando para 3 casas decimais
                            valor_GkDrive_Atual = round(pm.read_float(int(GkDriveMomentAddr, 16)), 3)
                            
                            # Comparando os valores com 3 casas decimais
                            if valor_GkDrive_Atual != GkDrive_Value:
                                # Escrevendo o novo valor na memória
                                pm.write_float(int(GkDriveMomentAddr, 16), GkDrive_Value)
                    except Exception:
                        print("Há algum problema com o GkDrive")
                        status_checks["gkdrive_ok"] = False



                except Exception as e:
                    print(f"Ocorreu um erro geral: {e}")


                # Define o intervalo de loop com base nos resultados das verificações
                if all(status_checks.values()):
                    loop_interval = 0.5 # Se todas as operações estiverem ok, intervalo de 0.5 segundo
                else:
                    loop_interval = 3.0  # Se houver falhas, intervalo de 5 segundos

                # Pausa o loop pelo intervalo definido
                time.sleep(loop_interval)



######################### HAND THROW

        
        def hand_throw(self):
            loop_handthrow = 5
            while True:
                try:
                    slider_valor = float(self._valorhandThrow.get())

                    # Aplica um fator especial se o slider estiver no máximo
                    if slider_valor >= 100:
                        valor_alvo_handThrow = 5.0  # Valor máximo arbitrário
                    else:
                        valor_alvo_handThrow = 1.0 + slider_valor / 100

                    if handthrowAddr and valor_alvo_handThrow != 1.0:
                        Valor_HandThrow1 = pm.read_float(int(handthrowAddr, 16))
                        if handthrowAddr != Valor_HandThrow1:
                            if 0.9 <= Valor_HandThrow1 <= 1.0:
                                pm.write_float(int(handthrowAddr, 16), valor_alvo_handThrow)

                        loop_handthrow = 0.08
                    else:
                        loop_handthrow = 2

                    time.sleep(loop_handthrow)

                except Exception as e:
                    self.after(1, print, f"Há algum problema com o Hand_Throw: {str(e)}")
                    loop_handthrow = 2

                time.sleep(loop_handthrow)





        # função do anti-kick

        def toggle_antikick(self):
            estado = self.valorAntiKick.get()

            if estado:
                pipeinject.enable_antikick(callback=lambda res, ok: None)
            else:
                pipeinject.disable_antikick(callback=lambda res, ok: None)


# //////////////////////////////////////////////////////
# ///////////== AS FUNÇÕES TERMIANM AQUI ==////////////
# ////////////////////////////////////////////////////



        
        
# //////////////////////////////////////////////////////
# ////////== AS THREADS SERÃO INICIADAS AQUI ==////////
# ////////////////////////////////////////////////////





        def start_funcao_geral_thread(self):
            global validation_status
            if not self.funcao_geral_thread or not self.funcao_geral_thread.is_alive():
                    self.funcao_geral_thread = threading.Thread(target=self.manage_game_values)
                    self.funcao_geral_thread.daemon = True
                    self.funcao_geral_thread.start()
                    print("Thread SPEED iniciada")


        def start_funcao_handthrow_thread(self):
            global validation_status
            if not self.funcao_handthrow_thread or not self.funcao_handthrow_thread.is_alive():
                    self.funcao_handthrow_thread = threading.Thread(target=self.hand_throw)
                    self.funcao_handthrow_thread.daemon = True
                    self.funcao_handthrow_thread.start()
                    print("Thread HandThrow iniciada")


        def start_funcao_verificador_thread(self):
            global validation_status
            if not self.funcao_verificador_thread or not self.funcao_verificador_thread.is_alive():
                self.funcao_verificador_thread = threading.Thread(target=self.verificador_processo)  # Correção: Não definir como `True`
                self.funcao_verificador_thread.daemon = True  # Isso faz a thread encerrar quando o programa principal termina
                self.funcao_verificador_thread.start()
                print("Thread Verificador iniciada")

                            


# //////////////////////////////////////////////////////
# ///////////== AS THREADS ACABA AQUI ==///////////////
# ////////////////////////////////////////////////////

        

            
 
        def add_slot(self):
            vaga_endereco = vagaAddr
            if vaga_endereco:
                try:
                    current_vaga_value = pm.read_int(int(vaga_endereco, 16))
                    new_vaga_value = current_vaga_value + 1
                    pm.write_int(int(vaga_endereco, 16), new_vaga_value)
                    print(f"Slot adicionado! Novo valor da vaga: {new_vaga_value}")
                except Exception as e:
                    print(f"Erro ao adicionar slot: {e}")
            else:
                print("Não é possível realizar esse comando")
            

        def kick_charge(self):
            estado_interruptor_kick_charge = self.valorInterruptor_kick_charge_key.get()

            if estado_interruptor_kick_charge:
                if kicktimeAddr or handthrowAddr or kickPositionAddr:
                    try:
                        # Valor dinâmico para hand throw baseado no slider
                        slider_valor = float(self._valorhandThrow.get())
                        valor_alvo_handThrow = 5.0 if slider_valor >= 100 else 1.0 + slider_valor / 100

                        # Execução do charge
                        for _ in range(18):
                            if kicktimeAddr:
                                pm.write_float(int(kicktimeAddr, 16), 30.0)
                            if kickPositionAddr:
                                pm.write_float(int(kickPositionAddr, 16), 1.0)
                            if handthrowAddr:
                                pm.write_float(int(handthrowAddr, 16), valor_alvo_handThrow)
                            time.sleep(0.05)

                        # Restaura valor final respeitando modo boost (2.0 = máximo)
                        kicking_value = float(self._valorKicking.get()) / 100
                        if kicktimeAddr:
                            if kicking_value == 2.0:
                                pm.write_float(int(kicktimeAddr, 16), 30.0)
                                if kickPositionAddr:
                                    pm.write_float(int(kickPositionAddr, 16), 1.0)
                            else:
                                pm.write_float(int(kicktimeAddr, 16), kicking_value)

                    except Exception as e:
                        print(f"Erro ao ativar kick charge: {e}")
                else:
                    print("Nenhum endereço disponível para kick charge.")





        def funcao_stamina_refil(self):
            estado_interruptor_stamina_key = self.valorInterruptor_stamina_key.get()
            if estado_interruptor_stamina_key:
                if staminaAddrCooldown:
                    pm.write_float(int(staminaAddrCooldown, 16), 1.0)
                    print("Stamina refilled!")

        def aplicar_configuracao_watermark(self):
            if self.valorCheckbox_watermark.get():
                pipeinject.enable_watermark()
            else:
                pipeinject.disable_watermark()

        def toggle_touchslow(self):
            if self.valorTouchSlow.get():
                pipeinject.disable_touchslow()
            else:
                pipeinject.enable_touchslow()


        # Função de verificação do processo e dos status
        def verificador_processo(self):
            while True:
                if not is_process_running():
                    print("O processo não está rodando")
                    os._exit(0)  # Sai do programa se o processo não estiver rodando
                else:
                    update_memory_addresses()

                time.sleep(2.0)


##testre
        # Funções para tornar a janela arrastável
        def start_move(self, event):
            """Inicia o movimento da janela."""
            self._offset_x = event.x
            self._offset_y = event.y

        def do_move(self, event):
            """Atualiza a posição da janela conforme o mouse se move."""
            x = self.winfo_pointerx() - self._offset_x
            y = self.winfo_pointery() - self._offset_y
            self.geometry(f"+{x}+{y}")

        def stop_move(self, event):
            """Termina o movimento da janela."""
            self._offset_x = 0
            self._offset_y = 0
##teste


        def minimizar(self):
            # Minimizar a janela
            self.withdraw()
            # Exibir uma message box com a tecla para reabrir o menu
            titulo = "PSOSENSE"
            mensagem = f"Press {menu_key_bind} to reopen the menu."
            # Exibir a messagebox
            messagebox.showinfo(titulo, mensagem)




    if __name__ == "__main__":
        app = App()
        app.mainloop()



# ////////////////////////////////////////////
# ////// Fim do Software Principal   ////////
# //////////////////////////////////////////

def validar_e_executar():
    import traceback  # <-- Adicione dentro da função
    global validation_status

    try:
        verificar_validade()

        if not validation_status:
            os._exit(0)
            raise RuntimeError("Security validation failed.")

        print("[OK] Security validation passed. Injecting DLL...")

        time.sleep(2)
        evento_injecao = threading.Event()

        def retorno_injecao(mensagem, sucesso):
            print(f"[INJECTION] {mensagem}")
            if sucesso:
                evento_injecao.set()
            else:
                raise RuntimeError("DLL injection failed: " + mensagem)

        try:
            pipeinject.inject_psosense_dll(callback=retorno_injecao)
        except Exception as e:
            raise RuntimeError(f"Injection process error: {e}")

        if evento_injecao.wait(timeout=10):
            print("[OK] Injection confirmed. Starting software in 1 second...")
            time.sleep(1)
            iniciar_software()
        else:
            raise TimeoutError("Timeout or failure in DLL injection.")

    except Exception:
        error_text = traceback.format_exc()
        error_notify.show_error_interface(error_text)

if __name__ == "__main__":
    try:
        verificador_web.initialize_browser_window()  # <- ATIVAR O LOADER
        validar_e_executar()                         # <- ATIVAR O VALIDADOR
    except Exception as e:
        import traceback
        error_text = traceback.format_exc()
        error_notify.show_error_interface(error_text)

