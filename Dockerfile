FROM python:3.12

# Atualiza e instala as dependências necessárias
RUN apt update && apt upgrade -y && \
    apt install -y python3-dev build-essential libmariadb-dev libmariadb-dev-compat git && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Clona o repositório
RUN git clone https://github.com/LucasKalil-Programador/PyCommander.git .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Instala o Gunicorn
RUN pip install gunicorn

# Comando para iniciar a aplicação
CMD ["gunicorn", "-w", "8", "-b", "127.0.0.1:8000", "main:app"]