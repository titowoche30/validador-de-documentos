# [START gae_python37_app]
# [START gae_python3_app]
from flask import Flask,render_template,flash
import pymysql

app = Flask(__name__)
app.config.from_pyfile('config.py')


from views import *

if __name__ == "__main__":
    # Só vai ser executado se o arquivo for executado diretamente, ou seja, se for importado não executa isso aqui
    #app.run(debug=True)
    app.run(host='127.0.0.1', port=8080) 

# [END gae_python3_app]
# [END gae_python37_app]