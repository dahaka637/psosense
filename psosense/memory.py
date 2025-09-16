import psutil
import ctypes
from ctypes import wintypes
from pymem import *
from pymem.process import *

# Indexadores globais (mantidos como constantes)
INDEXADORES = {
    "ULevel": [0x0030],
    "AWorldSettings": [0x0258],
    "TimeDilation": [0x02e8],
    "UGameInstance": [0x0180],
    "LocalPlayer": [0x0038],
    "APlayerController": [0x0030],
    "KickPower": [0x0610],
    "ASP_Character_C": [0x05c8],
    "Stamina": [0x06C8],
    "KickPowerTimeline": [0x05A0],
    "Kick_PlayRate": [0x00B8],
    "GkDriveMomentTimeline": [0x0648],
    "GkDriveMoment_Lenght": [0x00B4],
    "DribblingTimeline": [0x0590],
    "Dribbling_PlayRate": [0x00B8],
    "Dribbling_Position": [0x00bc],
    "Dribbling_Leght": [0x00b4],
    "JuggleTimeline": [0x0580],  
    "Juggle_PlayRate": [0x00B8], 
    "AMP_GameState_C": [0x05B8],
    "TeamSize": [0x032C],
    "UCameraComponent": [0x0558],
    "FieldOfView": [0x01F8],
    "USpringArmComponent": [0x00C0],
    "TargetArmLeght": [0x01f8],
    "KickPosition": [0x00bc],
    "KickLeght": [0x00b4]
}

class ProcessMemory:
    def __init__(self, process_name):
        self.process_name = process_name
        self.handle = None
        self.cache = {}  # Cache para endereços já calculados
    
    def get_process_handle(self):
        """Obtém o handle do processo através do nome."""
        if self.handle:
            return self.handle  # Reutilizar handle existente

        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if proc.info['name'] == self.process_name:
                pid = proc.info['pid']
                self.handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
                return self.handle
        return None
    
    def close_handle(self):
        """Fecha o handle do processo."""
        if self.handle:
            ctypes.windll.kernel32.CloseHandle(self.handle)
    
    def read_memory(self, address, size=8):
        """Lê a memória no endereço especificado e retorna o valor bruto."""
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t()
        
        result = ctypes.windll.kernel32.ReadProcessMemory(
            self.handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(bytes_read)
        )
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return buffer.raw

    def calculate_address(self, base_address, indexers):
        """Calcula o endereço final com base em um endereço base e uma lista de indexadores."""
        cache_key = (base_address, tuple(indexers))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        address = base_address
        for indexer in indexers:
            address += indexer
            address = int.from_bytes(self.read_memory(address), byteorder='little')
        self.cache[cache_key] = address
        return address

    def read_array(self, array_address, index):
        """Lê o array no endereço especificado e retorna o valor do índice desejado."""
        array_start = int.from_bytes(self.read_memory(array_address), byteorder='little')
        array_element = array_start + index * 8  # 8 bytes por elemento (ponteiros de 64 bits)
        return array_element



def montar_estrutura(gworld_base):
    """
    Função principal para montar a estrutura de endereços e retornar as variáveis renomeadas.
    :param gworld_base: Endereço base fornecido pela chamada externa.
    :return: Dicionário contendo os endereços como variáveis renomeadas.
    """
    process_name = "ProSoccerOnline-Win64-Shipping.exe"
    
    # Inicializa a classe para manipulação de memória
    process_memory = ProcessMemory(process_name)
    
    handle = process_memory.get_process_handle()
    
    if not handle:
        raise RuntimeError(f"Não foi possível obter o handle para o processo {process_name}.")
    
    try:
        # Funções auxiliares para obter endereços
        def calcular_com_indexadores(base, *indexadores):
            return process_memory.calculate_address(base, [INDEXADORES[i][0] for i in indexadores])

        # Inicializa as variáveis como None para garantir que possamos retornar mesmo em caso de erro
        address_data = {key: None for key in INDEXADORES}

        # Bloco para calcular speedAddr (TimeDilation)
        try:
            Ulevel = calcular_com_indexadores(gworld_base, "ULevel")
            AWorldSettings = calcular_com_indexadores(Ulevel, "AWorldSettings")
            address_data['speedAddr'] = AWorldSettings + INDEXADORES["TimeDilation"][0]
        except Exception:
            print("Erro ao calcular speedAddr")

        # Bloco para calcular UGameInstance e ULocalPlayer
        try:
            ugame_instance = calcular_com_indexadores(gworld_base, "UGameInstance")
            array_local_player = calcular_com_indexadores(ugame_instance, "LocalPlayer")
            ULocalPlayer = process_memory.read_array(array_local_player, 0)
        except Exception:
            ULocalPlayer = None
            print("Erro ao calcular ULocalPlayer")

        # Bloco para calcular APlayerController
        try:
            APlayerController = calcular_com_indexadores(ULocalPlayer, "APlayerController")
        except Exception:
            APlayerController = None
            print("Erro ao calcular APlayerController")

        # Bloco para calcular KickPower (handthrowAddr)
        try:
            address_data['handthrowAddr'] = APlayerController + INDEXADORES["KickPower"][0]
        except Exception:
            print("Erro ao calcular handthrowAddr")

        # Bloco para calcular vagaAddr (TeamSize)
        try:
            AMP_GameState_C = calcular_com_indexadores(APlayerController, "AMP_GameState_C")
            address_data['vagaAddr'] = AMP_GameState_C + INDEXADORES["TeamSize"][0]
        except Exception:
            print("Erro ao calcular vagaAddr")

        # Bloco para calcular FieldOfView (fovAddr)
        try:
            ASP_Character_C = calcular_com_indexadores(APlayerController, "ASP_Character_C")
            UCameraComponent = calcular_com_indexadores(ASP_Character_C, "UCameraComponent")
            address_data['fovAddr'] = UCameraComponent + INDEXADORES["FieldOfView"][0]
        except Exception:
            print("Erro ao calcular fovAddr")

        # Bloco para calcular Stamina (staminaAddrCooldown)
        try:
            address_data['staminaAddrCooldown'] = ASP_Character_C + INDEXADORES["Stamina"][0]
        except Exception:
            print("Erro ao calcular staminaAddrCooldown")

        # Bloco para calcular TargetArmLeght (cameraheightAddr)
        try:
            USpringArmComponent = calcular_com_indexadores(UCameraComponent, "USpringArmComponent")
            address_data['cameraheightAddr'] = USpringArmComponent + INDEXADORES["TargetArmLeght"][0]
        except Exception:
            print("Erro ao calcular cameraheightAddr")

        # Bloco para calcular KickPowerTimeline e Kick_PlayRate (kicktimeAddr)
        try:
            KickPowerTimeline = calcular_com_indexadores(APlayerController, "KickPowerTimeline")
            address_data['kicktimeAddr'] = KickPowerTimeline + INDEXADORES["Kick_PlayRate"][0]
            address_data['kickPositionAddr'] = KickPowerTimeline + INDEXADORES["KickPosition"][0]
            address_data['KickLeghtAddr'] = KickPowerTimeline + INDEXADORES["KickLeght"][0]
        except Exception:
            print("Erro ao calcular kicktimeAddr")

        # Bloco para calcular DribblingTimeline e Dribbling_PlayRate (dribblingAddr)
        try:
            DribblingTimeLine = calcular_com_indexadores(APlayerController, "DribblingTimeline")
            address_data['dribblingAddr'] = DribblingTimeLine + INDEXADORES["Dribbling_PlayRate"][0]
            address_data['dribblingPosition'] = DribblingTimeLine + INDEXADORES["Dribbling_Position"][0]
            address_data['dribblingLeght'] = DribblingTimeLine + INDEXADORES["Dribbling_Leght"][0]

        except Exception:
            print("Erro ao calcular dribblingAddr")

        # Bloco para calcular JuggleTimeline e Juggle_PlayRate (juggleAddr)
        try:
            JuggleTimeline = calcular_com_indexadores(APlayerController, "JuggleTimeline")
            address_data['juggleAddr'] = JuggleTimeline + INDEXADORES["Juggle_PlayRate"][0]
        except Exception:
            print("Erro ao calcular juggleAddr")

        # Bloco para calcular GkDriveMomentTimeline e GkDriveMoment_Lenght (GkDriveMomentAddr)
        try:
            GkDriveMomentTimeline = calcular_com_indexadores(ASP_Character_C, "GkDriveMomentTimeline")
            address_data['GkDriveMomentAddr'] = GkDriveMomentTimeline + INDEXADORES["GkDriveMoment_Lenght"][0]
        except Exception:
            print("Erro ao calcular GkDriveMomentAddr")

        # Retornar os endereços renomeados em hexadecimal ou None
        return {key: hex(val) if val else None for key, val in address_data.items()}

    except Exception as e:
        raise RuntimeError(f"Erro ao calcular os endereços: {e}")
    
    finally:
        process_memory.close_handle()
