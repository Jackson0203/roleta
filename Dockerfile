# Use a imagem base oficial do Python
FROM python:3.8-slim

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos do diretório atual para o contêiner
COPY . /app

# Instala as dependências do Python
RUN pip install -r requirements.txt

# Instala o Chrome Driver
RUN apt-get update && \
    apt-get install -y chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# Define a variável de ambiente para o caminho do Chrome Driver
ENV CHROME_DRIVER_PATH=/usr/bin/chromium-driver

# Comando padrão a ser executado quando o contêiner for iniciado
CMD ["python", "app.py"]
