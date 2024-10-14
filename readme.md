baixa a imagem mariadb -> docker pull mariadb:latest
primeira execucao do contaiiner -> docker run --name mariadb-container -p 3306:3306 -v /path/to/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=kalil2001kalil -d mariadb
iniciar o container -> docker start mariadb-container
executar comandos no container -> docker exec -it mariadb-container bash
