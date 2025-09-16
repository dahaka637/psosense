import sys
import hashlib
import os
import platform
import psutil
import string
import random
from PyQt6.QtCore import Qt, QUrl, QTimer, QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
import subprocess
import json

LoaderVersion = 4.5
hwid = hashlib.md5(platform.uname().node.encode()).hexdigest()
validation_status = False
chamada_concluida = False
process_name = "ProSoccerOnline-Win64-Shipping.exe"
user_email = None
license_time_remaining = 0
Email_Credential = None
Password_Credential = None


# //////////////////////////////////////////////////
# ////// Começo do Verificador de variável ////////
# ////////////////////////////////////////////////

def gerar_titulo_aleatorio(tamanho=16):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(tamanho))



class WebPage(QWebEnginePage):
    # ...restante do código da classe WebPage...

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """
        Manipula as mensagens do console JavaScript.
        """
        global chamada_concluida
        global user_email
        global license_time_remaining
        global Email_Credential
        global Password_Credential

        if not chamada_concluida:
            if "code507" in message:
                chamada_concluida = True
                self.validation_fail()

            if "Validation_Status: success" in message:
                if self.is_same_domain(sourceID, "psosense.web.app"):
                    if self.is_page_secure():
                        global validation_status
                        chamada_concluida = True
                        validation_status = True
                        self.validation_success()

           # Capturar o email do usuário e a senha
            if "Email:" in message or "Password:" in message:
                parts = message.split(":")
                if len(parts) > 1:
                    credential_type = parts[0].strip()
                    credential_value = parts[1].strip()
                    if credential_type == "Email":
                        Email_Credential = credential_value
                        print("email:", Email_Credential)
                    elif credential_type == "Password":
                        Password_Credential = credential_value
                        print("senha:", Password_Credential)

                    # Salvar as credenciais em um arquivo JSON
                    if Email_Credential and Password_Credential:
                        salvar_credenciais(Email_Credential, Password_Credential)

            # Capturar o tempo restante da licença
            if "timeleft:" in message:
                parts = message.split(":")
                if len(parts) > 1:
                    license_time_remaining = parts[1].strip()

            # Capturar o email do usuário
            if "EmailUsuario:" in message:
                parts = message.split(":")
                if len(parts) > 1:
                    user_email = parts[1].strip()



    def is_same_domain(self, url, target_domain):
        """
        Verifica se a URL está no mesmo domínio.
        """
        return QUrl(url).host() == target_domain

    def is_page_secure(self):
        """
        Verifica se a página está sendo carregada através de uma conexão segura (HTTPS).
        """
        return self.url().scheme().lower() == "https"
    
    def validation_fail(self):
        subprocess.call(['msg', '*', 'Software is outdated! Please contact support.'])
        QCoreApplication.quit()

    def validation_success(self):
        print("Função validation_success sendo chamada")
        if validation_status:
            print("A situação da variável está:", validation_status)
            self.check_process()

    def check_process(self):
        if is_process_running(process_name):
            print("Processo está rodando")
            QTimer.singleShot(1100, QCoreApplication.quit)
        else:
            QTimer.singleShot(1000, self.check_process)

def is_process_running(process_name):
    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'] == process_name:
            return True
    return False

# ///////////////////////////////////////////////
# ////// Fim do Verificador de variável ////////
# /////////////////////////////////////////////


# ////////////////////////////////////////////
# ////// Começo da Janela do Navegador ////////
# ////////////////////////////////////////////

class BrowserWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()

        # Adicionar informações à URL com base na existência de credenciais
        if Email_Credential is not None and Password_Credential is not None:
            modified_url = f"{url}?hwid={hwid}&version={LoaderVersion}&email={Email_Credential}&password={Password_Credential}"
        else:
            modified_url = f"{url}?hwid={hwid}&version={LoaderVersion}"

        print(modified_url)

        # Configurar a visualização web
        self.setup_web_view(modified_url)

        # Configurar a janela
        self.setup_window()

    def setup_web_view(self, url):
        """
        Configura a visualização web.
        """
        self.web_view = QWebEngineView()
        self.web_page = WebPage()
        self.web_view.setPage(self.web_page)
        self.web_view.setUrl(QUrl(url))
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # Conectar o evento de carregamento de página à função de ajuste de altura
        self.web_page.loadFinished.connect(self.adjust_window_height)

    def setup_window(self):
        """
        Configura a janela principal.
        """
        self.setCentralWidget(self.web_view)
        self.setWindowTitle(gerar_titulo_aleatorio())

        # Configurar o ícone da janela
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'img', 'LOGO.ico')))

        # Configurar a transparência
        self.setWindowOpacity(0.99)

        # Configurar as dimensões iniciais da janela
        self.setFixedSize(650, 600)

        self.show()

    def adjust_window_height(self):
        """
        Ajusta a altura da janela com base na página carregada.
        """
        current_url = self.web_page.url().toString()
        if "register.html" in current_url:
            self.setFixedHeight(650)
        elif "panel.html" in current_url:
            self.setFixedHeight(650)
        else:
            self.setFixedHeight(620)

# ////////////////////////////////////////////
# ////// Fim da Janela do Navegador ////////
# ////////////////////////////////////////////


# ////////////////////////////////////////////
# ////// Inicialização do Aplicativo /////////
# ////////////////////////////////////////////

def situacao_variaveis_seguranca():
    global validation_status
    return validation_status

def email_do_usuario():
    global user_email
    return user_email

def tempo_da_licenca():
    global license_time_remaining
    return license_time_remaining


def initialize_browser_window():
    try:
        # Verificar se o arquivo de credenciais existe
        script_dir = os.path.dirname(os.path.abspath(__file__))
        arquivo_json = os.path.join(script_dir, "credenciais_usuario.json")
        
        if os.path.exists(arquivo_json):
            with open(arquivo_json, 'r') as file:
                data = json.load(file)
                global Email_Credential, Password_Credential
                Email_Credential = data.get("email")
                Password_Credential = data.get("senha")
                print(f"Credenciais carregadas do arquivo {arquivo_json}")
        
        loader = QApplication(sys.argv)
        window = BrowserWindow("https://psosense.web.app/login.html")
        loader.exec()
    except Exception as e:
        print(f"Erro ao inicializar janela: {e}")




def salvar_credenciais(Email_Credential, Password_Credential):
    dados = {
        "email": Email_Credential,
        "senha": Password_Credential
    }
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        arquivo_json = os.path.join(script_dir, "credenciais_usuario.json")
        with open(arquivo_json, 'w') as file:
            json.dump(dados, file, indent=4)
        print(f"Credenciais do usuário salvas em {arquivo_json}")
    except Exception as e:
        print(f"Erro ao salvar as credenciais do usuário: {e}")

# ////////////////////////////////////////////
# ////// Fim da Inicialização ////////////////
# ////////////////////////////////////////////

#initialize_browser_window()
#teste#
