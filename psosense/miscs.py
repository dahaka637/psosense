############
# miscs.py
############
import os
import json
import random
import string

def salvar_configuracao(
    nome, valorDribbling, valorKicking, valorSpeed,
    interruptorStamina, interruptorStamina_Key,
    interruptorkickchargekey, kickchargekeybind,
    staminakeybind, menukeybind,
    valorFov, valorCameraHeight, valorHandTrow,
    valor_juggle, valor_GkDrive,
    interruptorSpawnBall, spawnballkeybind,
    interruptorAntiKick, valor_infinite_stamina, watermark,
    TouchSlow
):
    try:
        # Diretório onde o arquivo será salvo
        diretorio_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        print(f"Tentando acessar/criar o diretório: {diretorio_config}")

        # Se o diretório não existir, criar
        if not os.path.exists(diretorio_config):
            print(f"Diretório '{diretorio_config}' não existe, criando agora...")
            os.makedirs(diretorio_config)
        else:
            print(f"Diretório '{diretorio_config}' já existe.")

        # Montar o caminho completo do arquivo JSON com o nome da configuração
        caminho_arquivo = os.path.join(diretorio_config, f"{nome}.json")
        print(f"Tentando criar o arquivo em: {caminho_arquivo}")

        # Conteúdo a ser salvo no arquivo JSON
        conteudo = {
            "valorDribbling": valorDribbling,
            "valorKicking": valorKicking,
            "valorSpeed": valorSpeed,
            "interruptorStamina": interruptorStamina,
            "interruptorStamina_Key": interruptorStamina_Key,
            "interruptorkickchargekey": interruptorkickchargekey,
            "kickchargekeybind": kickchargekeybind,
            "staminakeybind": staminakeybind,
            "menukeybind": menukeybind,
            "valorFov": valorFov,
            "valorCameraHeight": valorCameraHeight,
            "valorHandTrow": valorHandTrow,
            "valorjuggle": valor_juggle,
            "valor_GkDrive": valor_GkDrive,
            "interruptorSpawnBall": interruptorSpawnBall,
            "spawnballkeybind": spawnballkeybind,
            "interruptorAntiKick": interruptorAntiKick,
            "valorInfiniteStamina": valor_infinite_stamina,
            "watermark": watermark,
            "TouchSlow": TouchSlow
        }

        # Salvar o arquivo JSON
        with open(caminho_arquivo, 'w') as arquivo:
            json.dump(conteudo, arquivo, indent=4)
        print(f"Arquivo '{nome}.json' criado com sucesso.")

    except Exception as e:
        print(f"Erro ao tentar criar o arquivo: {str(e)}")



def carregar_configuracao(nome):
    try:
        # Diretório onde o arquivo está salvo
        diretorio_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        caminho_arquivo = os.path.join(diretorio_config, f"{nome}.json")
        print(f"Tentando carregar o arquivo em: {caminho_arquivo}")

        # Verificar se o arquivo existe
        if os.path.exists(caminho_arquivo):
            # Carregar o arquivo JSON
            with open(caminho_arquivo, 'r') as arquivo:
                configuracao = json.load(arquivo)
            print(f"Configuração '{nome}.json' carregada com sucesso.")
            return configuracao
        else:
            print(f"Arquivo '{nome}.json' não encontrado.")
            return None

    except Exception as e:
        print(f"Erro ao tentar carregar o arquivo: {str(e)}")
        return None
