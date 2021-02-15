from modelos import User, File
from dao import FileDao, UserDao
from gcp_tools import create_storage_file
from main import app
from helpers import hashfile
from config import UPLOAD_PATH
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from MySQLdb._exceptions import IntegrityError
import os
import pymysql

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

def get_db():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user,
                                password=db_password,
                                db=db_name,
                                unix_socket=unix_socket
                        )
    except pymysql.MySQLError as e:
        print(e)

    return conn



'''
def get_db_local():
    try:
        conn = pymysql.connect(user=db_user, password=db_password,port = 3306, db=db_name, host = db_host)
    except pymysql.MySQLError as e:
        print(e)

    return conn
'''

db = get_db()
file_dao = FileDao(db)
user_dao = UserDao(db)

@app.route('/')
def index():
    return render_template('inicial.html')

@app.route('/public')
def public_page():
    return render_template('public-page.html')

@app.route('/validate',methods = ['POST'])
def validate_file():
    file_id = int(request.form['id'])
    file = request.files['file']

    file_name = file.filename.lower()
    if not file_name.endswith(('.png', '.jpeg', '.pdf', '.txt', '.docx')): 
        flash('Formato inválido de arquivo')
        return redirect(url_for('public_page'))


    file_obj = file_dao.search_by_id(file_id)
    if not isinstance(file_obj,File):
        flash('Arquivo não encontrado')
        return redirect(url_for('public_page'))

    # Pra conseguir o hash do arquivo, tenho que salva-lo, depois ler
    tmp_file_path = os.path.join(app.config['UPLOAD_PATH'],file.filename)
    file.save(tmp_file_path)
    with open(tmp_file_path,'rb') as f:
        uploaded_file_hash = hashfile(f.read())
    os.remove(tmp_file_path)
    
    # Checando se os hashs batem
    if uploaded_file_hash == file_obj.hash:
        flash('Arquivo validado com sucesso')
    else:
        flash('Arquivo inválido')

    
    return redirect(url_for('public_page'))

@app.route('/login')
def login():
    # .args são os argumentos que chegam nesse request
    #proxima = request.args['proxima']
    return render_template('login.html')

@app.route('/autenticar',methods=['POST'])
def autenticar():
    user_id = user_dao.get_user_id(request.form['user'])
    user = user_dao.search_by_id(user_id) 

    if user:
        if user.password == request.form['password']:
             # Cada usuário tem sua sessão
            session['user'] = user.id
            session['password'] = user.password
            session['login'] = user.login
            session['telefone'] = user.telefone
            flash(user.name + ' logado com sucesso')
            return redirect(url_for('user_screen'))
        else:
            flash('Senha incorreta')
            return redirect(url_for('login'))
    else:
        flash('Usuário não existente')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['user'] = None
    flash('Nenhum usuário logado')
    return redirect(url_for('index'))

@app.route('/create-user-form')
def create_user_form():
    return render_template('criar-user.html')

@app.route('/create-user', methods = ['POST'])
def create_user():
    name = request.form['name']   
    login = request.form['login']
    password = request.form['password']
    telefone = request.form['telefone']
    email = request.form['email']

    user = User(name,login,password,telefone,email)
    user_validate = user.valitade_fields()
    if not user_validate: 
        try:
            user = user_dao.save(user)
        except IntegrityError as e:
            flash('Usuário já existente')
            return redirect(url_for('create_user_form'))

        if isinstance(user,User): 
            flash('Usuário criado com sucesso')
            return redirect(url_for('index'))
    else: 
        flash(user_validate)
        return redirect(url_for('create_user_form'))


@app.route('/home')
def user_screen():
    user_id = session['user']
    if user_id is None:
        return redirect(url_for('index'))

    user = user_dao.search_by_id(user_id)
    files = file_dao.listing(user_id)

    extensoes = file_dao.listing_extensions(user_id)

    return render_template('files-list.html', files=files, user = user, extensoes = extensoes)


@app.route('/user-edit')
@app.route('/user-edit/<login>')
def user_edit(login=None):
    user_id = session['user']
    if user_id is None:
        return redirect(url_for('index'))

    if login:
        user = user_dao.search_by_login(login)
    else:
        user = user_dao.search_by_id(user_id)

    return render_template('editar-user.html',
    titulo = 'Editar dados',user = user)

@app.route('/user-update', methods = ['POST'])
def user_update():
    name = request.form['name']
    login = request.form['login']
    password = request.form['password']
    email = request.form['email']
    telefone = request.form['telefone']

    id = request.form['id']

    user = User(name,login,password,telefone,email,id=id)
    user_dao.save(user)

    flash('Informações atualizadas com sucesso')
    return redirect(url_for('index'))

@app.route('/user-delete')
@app.route('/user-delete/<login>')
def user_delete(login=None):
    user_id = session['user']
    if user_id is None:
        return redirect(url_for('index'))

    flag = url_for('index')
    if login:
        user = user_dao.search_by_login(login)
        user_id = user.id
        flag = url_for('user_screen')

    user_dao.delete(user_id)
    
    flash('O usuário foi removido com sucesso!')
    return redirect(flag)

@app.route('/user-read')
def user_read():
    user_id = session['user']
    if user_id is None:
        return redirect(url_for('index'))

    user = user_dao.search_by_id(user_id)
    return render_template('read-user.html',user=user)


@app.route('/create-file-form')
def create_file_form():
    user_id = session['user']
    if user_id is None:
        return redirect(url_for('index'))

    return render_template('criar-file.html')

@app.route('/create-file', methods = ['POST'])
def create_file():
    user_id = session['user']

    file = request.files['file'] 
    file_adress,hash = create_storage_file(file,user_id)
    file = File(file_adress,hash,user_id)
    file = file_dao.save(file)

    if isinstance(file,File):
        flash('Arquivo criado com sucesso')
        return redirect(url_for('user_screen'))
    else:
        flash('Não foi possível criar o arquivo')
        return redirect(url_for('create_file_form'))

@app.route('/filter-extension/<int:id>',methods=['POST'])
def filtrar_extensao(id):
    extensao = str(request.form.get('comp_select'))
    user = user_dao.search_by_id(id)
    files = file_dao.listing_by_extension(id,extensao)

    return render_template('files-list.html', files=files, user = user, extensoes = [extensao])


@app.route('/filter-name',methods=['POST'])
def filtrar_nome():
    nome = request.form['nome_do_arquivo']
    userid = request.form['id']
    user = user_dao.search_by_id(userid)
    files = file_dao.listing_by_name(int(userid),nome)

    extensoes = [] 
    for file in files: 
        extensoes.append(file.get_file_extension())

    return render_template('files-list.html', files=files, user = user, extensoes = extensoes)

@app.route('/edit-users')
def users_edit():
    user_login = session['login']

    if user_login != 'admin':
        flash('Você não tem permissão para acessar essa página')
        return redirect(url_for('user_screen'))
        
    return render_template('editar-users.html')

@app.route('/update-users',methods=['POST'])
def users_update():
    login = request.form['login']
    logins = user_dao.listing(1)
 
    if (login,) not in logins:
        flash('Login inválido')
        return redirect(url_for('users_edit'))

    return redirect(url_for('user_edit',login=login))

@app.route('/remove-users')
def users_remove():
    user_login = session['login']

    if user_login != 'admin':
        flash('Você não tem permissão para acessar essa página')
        return redirect(url_for('user_screen'))
        
    return render_template('remover-users.html')

@app.route('/delete-users',methods=['POST'])
def users_delete():
    login = request.form['login']
    logins = user_dao.listing(1)
 
    if (login,) not in logins:
        flash('Login inválido')
        return redirect(url_for('users_remove'))

    return redirect(url_for('user_delete',login=login))
