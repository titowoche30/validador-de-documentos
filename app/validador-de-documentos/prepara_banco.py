import psycopg2
from config import POSTGRES_HOST,POSTGRES_USER,POSTGRES_PASSWORD,POSTGRES_PORT,BUCKET_NAME

if __name__ == '__main__':
  print('Conectando...')
  conn = psycopg2.connect(f"user={POSTGRES_USER} dbname=postgres password={POSTGRES_PASSWORD} host={POSTGRES_HOST} port={POSTGRES_PORT}")
  conn.autocommit = True
  criar_banco = "CREATE DATABASE trab3"
  conn.cursor().execute(criar_banco)
  print('Banco trab3 criado')
  
  print('Conectando no banco trab3')
  conn = psycopg2.connect(f"user={POSTGRES_USER} dbname=trab3 password={POSTGRES_PASSWORD} host={POSTGRES_HOST} port={POSTGRES_PORT}")
  conn.autocommit = True

  criar_tabela_usuario =  ''' CREATE TABLE Usuario (
        id serial,
        name varchar(100) NOT NULL,
        login varchar(20) UNIQUE NOT NULL,
        password varchar(20) NOT NULL,
        email varchar(30) NOT NULL,
        PRIMARY KEY (id)
      ) '''

  criar_tabela_file = ''' CREATE TABLE File (
        id serial,
        userid integer NOT NULL,
        file varchar(1000) NOT NULL,
        hash varchar(300), 
        PRIMARY KEY (id),
        FOREIGN KEY (userid) REFERENCES Usuario(id) ON DELETE CASCADE,
        UNIQUE (userid,hash)
      ) '''

  conn.cursor().execute(criar_tabela_usuario)
  print('Tabela User criada')
  conn.cursor().execute(criar_tabela_file)
  print('Tabela File criada')
