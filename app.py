from flask import Flask, render_template
from flask_socketio import SocketIO
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import threading
from datetime import datetime

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)  # Inicialize o SocketIO
resultados = []
ultimo_id_resultado = 0

@app.route('/')
def index():
    return render_template('index.html', resultados=resultados)

def coletar_dados():
    while True:
        today = datetime.now().strftime("%Y-%m-%d")
        url = "https://casino.betfair.com/pt-br/c/roleta"

        try:
            servico = Service(ChromeDriverManager().install())
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(service=servico, options=chrome_options)
            driver.implicitly_wait(10)

            driver.get(url)

            while True:
                try:
                    roulette_element = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/span[1]")
                    roulette_number = roulette_element.text.strip()
                    current_time = time.strftime("%H:%M:%S", time.localtime())
                    resultado = {
                        'data': today,
                        'conteudo': f"{current_time}: {roulette_number}"
                    }

                    resultados.append(resultado)

                    # Emite o novo resultado via SocketIO
                    socketio.emit('novo_resultado', resultado)

                    time.sleep(50)

                except NoSuchElementException:
                    print("Elemento da roleta não encontrado")
                    break

            driver.quit()

        except Exception as e:
            print("Ocorreu um erro durante a execução:", str(e))

if __name__ == "__main__":
    thread_coleta = threading.Thread(target=coletar_dados)
    thread_coleta.start()

    # Adicione as configurações para permitir WebSocket
    socketio.run(app, host='0.0.0.0', port=10000)
