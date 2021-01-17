from flask import Flask,render_template
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = MySQL(app)

#@app.route('/')
#def index():
#    return render_template('inicial.html')


from views import *
 
if __name__ == "__main__":
    # Só vai ser executado se o arquivo for executado diretamente, ou seja, se for importado não executa isso aqui
    app.run(debug=True) 
