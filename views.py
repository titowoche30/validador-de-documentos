from modelos import User, File
from dao import FileDao, UserDao
from aws_tools import *
from flaskapp import db,app
from helpers import hashfile
from config import UPLOAD_PATH
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from flask_mysqldb import MySQL
import os
from MySQLdb._exceptions import IntegrityError

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
    file_id = request.form['id']
    motive = request.form['motive']
    file = request.files['file']

    file_name = file.filename.lower()
    if not file_name.endswith(('.png', '.jpeg', '.pdf')): 
        flash('Arquivo no formato inválido')
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
    pos_val_flag, neg_val_flag = 0,0
    if uploaded_file_hash == file_obj.hash:
        flash('Arquivo validado com sucesso')
        pos_val_flag = 1
    else:
        flash('Arquivo não-válido')
        neg_val_flag = 1

    write_to_dynamo(file_id,motive,pos_val_flag,neg_val_flag)

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
    # Quando erra senha mostra usuário não existente
 
    if user:
        if user.password == request.form['password']:
             # Cada usuário tem sua sessão
            session['user'] = user.id
            session['password'] = user.password
            session['login'] = user.login

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
    email = request.form['email']

    user = User(name,login,password,email)

    try:
        user = user_dao.save(user)
    except IntegrityError as e:
        flash('Usuário já existente')
        return redirect(url_for('create_user_form'))


    if isinstance(user,User): 
        flash('Usuário criado com sucesso')
        return redirect(url_for('index'))

@app.route('/home')
def user_screen():
    user_id = session['user']
    if user_id is None:
        return redirect(url_for('index'))

    user = user_dao.search_by_id(user_id)
    files = file_dao.listing(user_id)

    new_files = set_files_val(files)

    return render_template('files-list.html', files=new_files, user = user)


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
    id = request.form['id']

    user = User(name,login,password,email,id=id)
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
    delete_s3_user_folder(user_id)
    
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
    user_id,file_adress,hash = create_s3_file(file,user_id)
    file = File(user_id,file_adress,hash)
    file = file_dao.save(file)

    if isinstance(file,File):
        flash('Arquivo criado com sucesso')
        return redirect(url_for('user_screen'))
    else:
        print('\n\n-----OLÁ------\n\n')


@app.route('/edit-file/<int:id>')
def edit_file(id):  
    user_id = session['user']
    if user_id is None:
        return redirect(url_for('index'))

    file = file_dao.search_by_id(id)

    if not file:
        flash('Esse arquivo não existe')
        return redirect(url_for('user_screen'))

    if user_id != file.userid and user_id != 1:
        flash('Você não tem permissão para editar esse arquivo')
        return redirect(url_for('user_screen'))


    return render_template('editar-file.html',
    titulo = f'Editar arquivo {file.get_key()}',file = file)

@app.route('/update-file', methods = ['POST'])
def update_file():
    user_id = request.form['user_id']
    file_adress = request.form['file_adress']
    id = request.form['id']
    file = request.files['file']

    file_id = delete_s3_file(file_adress,id)
    delete_file_from_dynamo(id)

    user_id,file_adress,hash = create_s3_file(file,user_id)

    file = File(user_id,file_adress,hash,id=file_id)
    file = file_dao.save(file)

    if isinstance(file,File):
        flash('Arquivo atualizado com sucesso')
        return redirect(url_for('user_screen'))

    flash('Arquivo atualizado com sucesso')
    return redirect(url_for('user_screen'))

@app.route('/file-delete/<int:id>')
def delete_file(id):
    user_id = session['user']

    if user_id is None:
        return redirect(url_for('index'))

    file = file_dao.search_by_id(id)

    if not file:
        flash('Esse arquivo não existe')
        return redirect(url_for('user_screen'))

    if user_id != file.userid and user_id != 1:
        flash('Você não tem permissão para deletar esse arquivo')
        return redirect(url_for('user_screen'))

    delete_s3_file(file.file,id)
    delete_file_from_dynamo(file.id)

    file_dao.delete(id)

    flash('O arquivo foi removido com sucesso!')
    return redirect(url_for('user_screen'))


@app.route('/file-log/<int:id>')
def file_log(id):
    user_id = session['user']

    if user_id is None:
        return redirect(url_for('index'))

    file = file_dao.search_by_id(id)

    if not file:
        flash('Esse arquivo não existe')
        return redirect(url_for('user_screen'))

    if user_id != file.userid and user_id != 1:
        flash('Você não tem permissão para gerar esse log')
        return redirect(url_for('user_screen'))

    if not generate_log(file):
        flash('Impossível gerar log, nenhuma validação foi feita para esse arquivo.')
        return redirect(url_for("user_screen"))

    return send_from_directory(f'{UPLOAD_PATH}','log.csv', as_attachment = True)

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


#TODO Load balancing quando já tiver no EC2
