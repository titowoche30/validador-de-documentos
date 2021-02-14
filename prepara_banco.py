import MySQLdb
from config import MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_PORT,BUCKET_NAME
print('Conectando...')
conn = MySQLdb.connect(user=MYSQL_USER, passwd=MYSQL_PASSWORD, host=MYSQL_HOST, port=MYSQL_PORT)

# Descomente se quiser desfazer o banco...
# conn.cursor().execute("DROP DATABASE `trab1`;")
# conn.commit()


criar_tabelas = '''SET NAMES utf8;
    SET CHARACTER SET utf8;
    CREATE DATABASE `trab2` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;
    USE `trab2`;
    CREATE TABLE `User` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(100) COLLATE utf8_bin NOT NULL,
      `login` varchar(20) COLLATE utf8_bin UNIQUE NOT NULL,
      `password` varchar(20) NOT NULL,
      `telefone` varchar(20) NOT NULL,
      `email` varchar(30) NOT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;'''

conn.cursor().execute(criar_tabelas)
conn.commit()

