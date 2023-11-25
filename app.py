from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import threading
from flask import Flask, render_template_string
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)
resultados = []
ultimo_id_resultado = 0  # Rastreia o último ID de resultado

# Template HTML incorporado
template_html = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultados da Roleta</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.0.7/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        .column {
            margin-bottom: 20px;
        }
    </style>
    <script>
        var socket = io.connect('http://' + document.domain + ':' + location.port + '/resultado');

        socket.on('connect', function() {
            console.log('Conectado ao servidor WebSocket');
        });

        socket.on('novo_resultado', function(resultado) {
            // Adicione o novo resultado à lista de resultados
            var resultadosLista = document.getElementById('resultados-lista');
            var novoResultado = document.createElement('li');
            novoResultado.innerText = resultado['conteudo'];
            resultadosLista.appendChild(novoResultado);
        });
    </script>
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Resultados da Roleta</h1>
        <div id="resultados-lista" class="row">
            {% for data, resultados_do_dia in resultados_por_data.items() %}
                <div class="col-md-4">
                    <div class="card column">
                        <div class="card-header">
                            <h2>{{ data }}</h2>
                        </div>
                        <ul class="list-group list-group-flush">
                            {% for resultado in resultados_do_dia %}
                                <li class="list-group-item">{{ resultado }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Organize os resultados por data
    resultados_por_data = {}
    for resultado in resultados:
        data = resultado['data']
        if data not in resultados_por_data:
            resultados_por_data[data] = []
        resultados_por_data[data].append(resultado['conteudo'])

    # Renderizar diretamente no Python
    return render_template_string(template_html, resultados_por_data=resultados_por_data)

def coletar_dados():
    while True:
        # Obtém a data atual
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

                    socketio.emit('novo_resultado', resultado, namespace='/resultado')

                    time.sleep(50)

                except NoSuchElementException:
                    print("Elemento da roleta não encontrado")
                    break

                except KeyboardInterrupt:
                    print("Programa interrompido pelo usuário")
                    break

            driver.quit()

        except Exception as e:
            print("Ocorreu um erro durante a execução:", str(e))

if __name__ == "__main__":
    thread_coleta = threading.Thread(target=coletar_dados)
    thread_coleta.start()

    socketio.run(app, host='0.0.0.0', port=10000)
