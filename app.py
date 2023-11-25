from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)
resultados = []
ultimo_id_resultado = 0  # Rastreia o último ID de resultado

# Flag para controlar o encerramento do programa
encerrar_programa = False

@app.route('/')
def index():
    # Organize os resultados por data
    resultados_por_data = {}
    for resultado in resultados:
        data = resultado['data']
        if data not in resultados_por_data:
            resultados_por_data[data] = []
        resultados_por_data[data].append(resultado['conteudo'])

    return render_template('index.html', resultados_por_data=resultados_por_data)

def coletar_dados():
    while not encerrar_programa:
        # Obtém a data atual
        today = datetime.now().strftime("%Y-%m-%d")

        url = "https://casino.betfair.com/pt-br/c/roleta"

        try:
            servico = Service(ChromeDriverManager().install())
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(service=servico, options=chrome_options)
            # Definir um tempo limite para esperar até que o elemento seja encontrado
            driver.implicitly_wait(10)  # Aguarda até 10 segundos por elementos

            # Fazer a requisição GET para a página
            driver.get(url)

            while not encerrar_programa:
                try:
                    roulette_element = driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/span[1]")
                    roulette_number = roulette_element.text.strip()
                    current_time = time.strftime("%H:%M:%S", time.localtime())
                    resultado = {
                        'data': today,
                        'conteudo': f"{current_time}: {roulette_number}"
                    }

                    # Adicione o resultado à lista de resultados
                    resultados.append(resultado)

                    # Envie a mensagem via WebSocket quando um novo resultado estiver disponível
                    socketio.emit('novo_resultado', resultado, namespace='/resultado')

                    time.sleep(50)  # Aguarda 50 segundos antes de buscar o próximo resultado

                except NoSuchElementException:
                    print("Elemento da roleta não encontrado")
                    break

            # Fechar o driver do Selenium
            driver.quit()

        except Exception as e:
            print("Ocorreu um erro durante a execução:", str(e))

if __name__ == "__main__":
    # Crie uma thread para coletar dados
    thread_coleta = threading.Thread(target=coletar_dados)
    thread_coleta.start()

    try:
        # Inicie o servidor SocketIO para permitir a comunicação em tempo real
        socketio.run(app, host='0.0.0.0', port=10000)
    except KeyboardInterrupt:
        print("Encerrando o programa...")
        encerrar_programa = True
        thread_coleta.join()
        socketio.stop()
