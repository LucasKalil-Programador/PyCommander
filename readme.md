baixa a imagem mariadb -> docker pull mariadb:latest
primeira execucao do contaiiner -> docker run --name mariadb-container -p 3306:3306 -v /path/to/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=kalil2001kalil -d mariadb
iniciar o container -> docker start mariadb-container
executar comandos no container -> docker exec -it mariadb-container bash


git clone https://github.com/LucasKalil-Programador/PyCommander.git
sudo apt install python3-dev build-essential libmariadb-dev libmariadb-dev-compat python3 python3-venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

