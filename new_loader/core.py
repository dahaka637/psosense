from PyQt6.QtCore import QThread, pyqtSignal
import requests
import time

class ValidationWorker(QThread):
    result_signal = pyqtSignal(dict)     # Resultado final
    status_signal = pyqtSignal(str)      # Atualizações ao vivo (status)

    def __init__(self, key: str, hwid: str):
        super().__init__()
        self.key = key
        self.hwid = hwid
        self.retry_interval = 1  # Tempo entre as tentativas (em segundos)

    def run(self):
        payload = {
            "key": self.key,
            "product": "crasher",  # Nome fixo do produto usado no backend
            "hwid": self.hwid
        }

        while True:
            self.status_signal.emit("Trying to connect to license server...")

            try:
                response = requests.post(
                    "http://181.215.45.160:5000/activate",
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                else:
                    result = {
                        "status": "error",
                        "message": f"HTTP {response.status_code}: {response.text}"
                    }

                self.result_signal.emit(result)
                break  # Finaliza a thread após resposta válida

            except requests.exceptions.Timeout:
                self.status_signal.emit("Timeout. Retrying in 1 seconds...")
            except requests.exceptions.ConnectionError:
                self.status_signal.emit("Connection failed. Retrying in 1 seconds...")
            except Exception as e:
                self.status_signal.emit(f"Unexpected error: {e}. Retrying...")

            time.sleep(self.retry_interval)
