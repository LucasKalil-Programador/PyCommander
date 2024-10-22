### Configuration .env
Para que este servidor seja executado corretamente, é necessário configurar o arquivo [_.env.example_](.env.example) presente na pasta raiz do projeto. Esse arquivo deve ser configurado e renomeado para [_.env_]() para que o sistema funcione adequadamente

Siga as instruções abaixo para configurar o [_.env_]() . Este arquivo é dividido em três principais regiões: Database, JWT e Default User

Na configuração do Database, você deve alterar `db_host_ip` para o IP e porta do banco de dados MariaDB. Também deve alterar `db_user` e `db_password` para os que você escolheu ao criar o banco de dados. Não é necessário alterar `db_name`
```yaml
# Database configuration
db_host_ip=127.0.0.1
db_port=3306
db_user=root
db_password=your_db_password
db_name=restaurant_db
```

Na configuração do JWT, apenas é necessário alterar a `JWT_SECRET_KEY` para uma senha secreta, a fim de evitar problemas de segurança. No entanto, se desejar, você pode experimentar outros valores: `JWT_ACCESS_TOKEN_EXPIRES_MINUTES`, que controla o tempo até que o token expire, e `JWT_REFRESH_TOKEN_EXPIRES_DAYS`, que controla a validade do token de refresh para gerar um novo access token
```yaml
# JWT configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRES_DAYS=7
```

Na configuração do Default User, os valores são usados para criar um usuário admin padrão ao iniciar o servidor e o banco de dados pela primeira vez. É importante alterar esse usuário o mais rápido possível após criar o servidor
```yaml
# Default user
DEFAULT_USER=default_user
DEFAULT_PASSWORD=default_password
```

### Instalação do Docker (Recomendado)

O Docker é um software de virtualização de contêineres, permitindo criar ambientes isolados para cada parte do projeto. Aqui, vou dar uma breve explicação de como executar o PyCommander em um ambiente Docker

Primeiramente, certifique-se de que tem o Docker instalado em um ambiente Linux, preferencialmente Ubuntu. Isso também pode ser feito em um ambiente WSL2 no Windows, que foi utilizado para este projeto

Caso não tenha instalado, siga o passo a passo presente em [docs.docker.com/engine/install](https://docs.docker.com/engine/install/)

```bash
# Verifica se o docker esta instalado
docker --version

# Baixa a imagem do banco de dados MariaDB
docker pull mariadb:latest

# Primeira execução do MariaDB; substitua <your_password_here> pela sua senha
docker run --name mariadb-container -p 3306:3306 -v /path/to/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=<your_password_here> -d mariadb

# Inicia o banco de dados
docker start mariadb-container
```

Com o MariaDB instalado corretamente, siga para a instalação do contêiner Python:

```bash
# Primeiramente, faça um git clone desse repositório para o seu ambiente Linux
git clone https://github.com/LucasKalil-Programador/PyCommander.git

# Configure o .env.example
nano .env.example

# Não se esqueça de configurar corretamente e depois altere o nome do arquivo para .env
mv .env.example .env

# Navegue até a pasta do projeto 
cd PyCommander

# Crie a imagem do contêiner com as especificações presentes no Dockerfile
docker build -t py_commander_app .

# Execute o contêiner recém-criado
docker run --rm -p 8000:8000 -v $(pwd)/.env:/app/.env py_commander_app
```

Com isso, você deve ter um banco de dados MariaDB rodando na porta 3306 e um servidor Python na porta 8000

### Instalação Linux/Windows

Caso prefira instalar diretamente em um ambiente Linux ou Windows, siga os seguintes passos:

Instale o [Python3](https://www.python.org/downloads/) e o [MariaDB](https://mariadb.com/kb/en/getting-installing-and-upgrading-mariadb/) seguindo seus respectivos passos a passo.

Com o Python e o MariaDB instalados:

#### Linux:
```bash
# Clone o repositório do projeto
git clone https://github.com/LucasKalil-Programador/PyCommander.git

# Atualize os pacotes
sudo apt update && sudo apt upgrade

# Instale dependências para a build do Python
sudo apt install python3-dev build-essential libmariadb-dev libmariadb-dev-compat python3 python3-venv

# Crie um ambiente Python isolado
python3 -m venv .venv

# Ative o ambiente virtual
source .venv/bin/activate

# Baixe os requisitos
pip install -r requirements.txt

# Configure o .env.example
nano .env.example

# Não se esqueça de configurar corretamente e depois altere o nome do arquivo para .env
mv .env.example .env

# Execute o projeto
python3 main.py
```
Para Linux, você ainda tem a opção de executar em um servidor Gunicorn. A vantagem dessa abordagem é a possibilidade de executar em múltiplas threads, respondendo às requests. Com a instalação via Docker, o Gunicorn já é implementado por padrão
```bash
# Instale o Gunicorn
pip install gunicorn

# Rode o projeto com o comando. Este comando executa 8 workers, o que garante melhor performance para o servidor
gunicorn -w 8 -b 127.0.0.1:8000 main:app
```

#### Windows
```bash
# Clone o repositório do projeto
git clone https://github.com/LucasKalil-Programador/PyCommander.git

# Instale o Virtualenv (caso não tenha)
pip install virtualenv

# Navegue até o diretório do projeto
cd PyCommander

# Crie um ambiente Python isolado
python -m venv .venv

# Ative o ambiente virtual
.venv\Scripts\activate

# Configure o .env.example
nano .env.example

# Não se esqueça de configurar corretamente e depois altere o nome do arquivo para .env
mv .env.example .env

# Execute o projeto
python main.py
```

