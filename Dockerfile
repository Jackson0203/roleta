# Use a imagem base oficial do Python
FROM python:3.8-slim

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos do diretório atual para o contêiner
COPY . /app

# Instala as dependências do Python
RUN pip install -r requirements.txt

# Atualiza os pacotes e instala as dependências necessárias
RUN apt-get update && \
    apt-get install -y gnupg2 wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Adiciona a chave GPG para o repositório do Chromium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Instala o Chromium
RUN apt-get update && \
    apt-get install -y chromium && \
    rm -rf /var/lib/apt/lists/*

# Define a variável de ambiente para o caminho do Chrome Driver
ENV CHROME_DRIVER_PATH=/usr/lib/chromium/chromedriver

# Comando padrão a ser executado quando o contêiner for iniciado
CMD ["python", "app.py"]
