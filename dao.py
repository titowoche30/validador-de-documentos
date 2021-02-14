from modelos import User, File
from google.cloud import storage
from google.cloud import datastore
import pymysql

SQL_CREATE_USER = 'INSERT INTO User (name, login, password, telefone, email) VALUES (%s, %s, %s, %s,%s)'
SQL_READ_USER = 'SELECT id, name, login, password, telefone, email FROM User WHERE id = %s'
SQL_READ_USER_LOGIN = 'SELECT id, name, login, password, telefone, email FROM User WHERE login = %s'
SQL_UPDATE_USER = 'UPDATE User SET name=%s, login=%s, password=%s, telefone=%s, email=%s WHERE id = %s'
SQL_DELETE_USER = 'DELETE FROM User WHERE id = %s'
SQL_SEARCH_USERS = 'SELECT id, name, login, password, telefone, email FROM User'
SQL_SEARCH_USER = 'SELECT id, name, login, password, telefone, email FROM User WHERE login = %s'
SQL_SEARCH_LOGINS = 'SELECT login FROM User'

storage_client = storage.Client()
datastore_client = datastore.Client()

def get_file_object(link,hash,userid,id):
    return File(link,hash, userid, id = id)

def get_user_object(field):
    return User(field[1], field[2], field[3], field[4], field[5], id = field[0])

class FileDao:
    def __init__(self, db):
        self.__db = db

    def save(self, file):

        key = datastore_client.key('id')
        entity = datastore.Entity(key=key)
        entity.update({
            'Userid': file.userid,
            'Hash': file.hash,
            'Link': file.file,
            'Format': file.file.split('.')[-1],
            'Name': file.file.split('/')[-1].split('.')[0]
        })
        datastore_client.put(entity)

        return file

    def listing(self,userid=None):
        files = []
        query = datastore_client.query(kind='id')

        if userid and userid != 1 : query.add_filter('Userid', '=', userid)

        query_iter = query.fetch()
        for entity in query_iter:
            files.append(get_file_object(entity['Link'],entity['Hash'],entity['Userid'],entity.id))

        return files

    def listing_extensions(self,userid):
        extensions = []
        query = datastore_client.query(kind='id')
        
        if userid != 1 : query.add_filter('Userid', '=', userid)

        query_iter = query.fetch()

        for entity in query_iter:
            extensions.append(entity['Format'])

        return extensions


    def listing_by_extension(self,user,extension):
        files = []
        query = datastore_client.query(kind='id')
        query.add_filter('Format', '=', extension)

        query_iter = query.fetch()
        for entity in query_iter:
            files.append(get_file_object(entity['Link'],entity['Hash'],entity['Userid'],entity.id))

        return files

    def listing_by_name(self,user,name):
        files = []
        query = datastore_client.query(kind='id')
        query.add_filter('Name', '=', name)

        query_iter = query.fetch()
        for entity in query_iter:
            files.append(get_file_object(entity['Link'],entity['Hash'],entity['Userid'],entity.id))

        return files

    def search_by_id(self, id):
        key = datastore_client.key('id', id)
        query = datastore_client.query(kind='id')
        query.key_filter(key,'=') 
        query_iter = query.fetch(1)

        for entity in query_iter:
            return get_file_object(entity['Link'],entity['Hash'],entity['Userid'],entity.id) 

        

class UserDao:
    def __init__(self, db):
        self.__db = db

    def save(self, user):
        cursor = self.__db.cursor()

        if (user.id):
            cursor.execute(SQL_UPDATE_USER, (user.name, user.login, user.password, user.telefone, user.email,user.id))
        else:
            cursor.execute(SQL_CREATE_USER, (user.name, user.login, user.password, user.telefone,user.email))
            user.id = cursor.lastrowid 
        self.__db.commit()
        return user

    def listing(self,user_id = None):
        cursor = self.__db.cursor()
        
        if user_id == 1:
            cursor.execute(SQL_SEARCH_LOGINS)
            logins = cursor.fetchall()
            return logins

        cursor.execute(SQL_SEARCH_USERS)
        user = get_user_object(cursor.fetchall())
        return user

    def search_by_id(self, id):
        cursor = self.__db.cursor()
        cursor.execute(SQL_READ_USER, (str(id),))
        data = cursor.fetchone()
        user = get_user_object(data) if data else None
        return user

    def search_by_login(self, login):
        cursor = self.__db.cursor()
        cursor.execute(SQL_READ_USER_LOGIN, (login,))
        data = cursor.fetchone()
        user = get_user_object(data) if data else None
        return user

    def get_user_id(self,login):
        cursor = self.__db.cursor()
        cursor.execute(SQL_SEARCH_USER, (login,))
        field = cursor.fetchone()
        return field[0] if field else None 

    def delete(self, id):
        self.__db.cursor().execute(SQL_DELETE_USER, (id,))
        self.__db.commit()

