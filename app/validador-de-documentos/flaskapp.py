from flask import Flask,render_template
from config import POSTGRES_HOST,POSTGRES_USER,POSTGRES_PASSWORD,POSTGRES_PORT
import psycopg2

app = Flask(__name__)
app.config.from_pyfile('config.py')

conn = psycopg2.connect(f"user={POSTGRES_USER} dbname=trab3 password={POSTGRES_PASSWORD} host={POSTGRES_HOST} port={POSTGRES_PORT}")
conn.autocommit = True
# conn = execute()

from views import *
 
if __name__ == "__main__":
    # Só vai ser executado se o arquivo for executado diretamente, ou seja, se for importado não executa isso aqui
    
    app.run(debug=True,port=5000,host='0.0.0.0') 
