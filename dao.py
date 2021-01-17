from modelos import User, File

SQL_CREATE_FILE = 'INSERT INTO File (userid, file, hash) VALUES (%s, %s, %s)'
SQL_READ_FILE = 'SELECT id, userid, file, hash FROM File where id = %s'
SQL_READ_FILE_USER = 'SELECT id, userid, file, hash FROM File where userid = %s'
SQL_READ_ALL_FILES = 'SELECT id, userid, file, hash FROM File'


SQL_UPDATE_FILE = 'UPDATE File SET userid=%s, file=%s, hash=%s WHERE id = %s'
SQL_DELETE_FILE = 'DELETE FROM File WHERE id = %s'
SQL_SEARCH_FILES = 'SELECT id, userid, file, hash FROM File'

SQL_CREATE_USER = 'INSERT INTO User (name, login, password, email) VALUES (%s, %s, %s, %s)'
SQL_READ_USER = 'SELECT id, name, login, password, email FROM User WHERE id = %s'
SQL_READ_USER_LOGIN = 'SELECT id, name, login, password, email FROM User WHERE login = %s'
SQL_UPDATE_USER = 'UPDATE User SET name=%s, login=%s, password=%s, email=%s WHERE id = %s'
SQL_DELETE_USER = 'DELETE FROM User WHERE id = %s'
SQL_SEARCH_USERS = 'SELECT id, name, login, password, email FROM User'
SQL_SEARCH_USER = 'SELECT id, name, login, password, email FROM User WHERE login = %s'
SQL_SEARCH_LOGINS = 'SELECT login FROM User'


def get_files_objects(files):
    def create_file_with_tuple(fields):
        return File(fields[1], fields[2], fields[3], id = fields[0])
    return list(map(create_file_with_tuple, files))

def get_user_object(field):
    return User(field[1], field[2], field[3], field[4], id = field[0])

class FileDao:
    def __init__(self, db):
        self.__db = db

    def save(self, file):
        cursor = self.__db.connection.cursor()

        if (file.id):
            cursor.execute(SQL_UPDATE_FILE, (file.userid, file.file, file.hash, file.id))
        else:
            cursor.execute(SQL_CREATE_FILE, (file.userid, file.file,file.hash))
            file.id = cursor.lastrowid

        self.__db.connection.commit()
        return file

    def listing(self,userid=None):
        cursor = self.__db.connection.cursor()
        if userid: 
            cursor.execute(SQL_READ_FILE_USER,(userid,))
            if userid == 1:
                cursor.execute(SQL_READ_ALL_FILES)
        else: 
            cursor.execute(SQL_SEARCH_FILES)

        files = get_files_objects(cursor.fetchall())
        return files

    def search_by_id(self, id):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_READ_FILE, (id,))
        fields = cursor.fetchone() 
        return File(fields[1], fields[2], fields[3], id = fields[0]) if fields else None

    def delete(self, id):
        self.__db.connection.cursor().execute(SQL_DELETE_FILE, (id,))
        self.__db.connection.commit()


class UserDao:
    def __init__(self, db):
        self.__db = db

    def save(self, user):
        cursor = self.__db.connection.cursor()

        if (user.id):
            cursor.execute(SQL_UPDATE_USER, (user.name, user.login, user.password,user.email,user.id))
        else:
            cursor.execute(SQL_CREATE_USER, (user.name, user.login, user.password,user.email))
            user.id = cursor.lastrowid
        self.__db.connection.commit()
        return user

    def listing(self,user_id = None):
        cursor = self.__db.connection.cursor()
        
        if user_id == 1:
            cursor.execute(SQL_SEARCH_LOGINS)
            logins = cursor.fetchall()
            return logins

        cursor.execute(SQL_SEARCH_USERS)
        user = get_user_object(cursor.fetchall())
        return user

    def search_by_id(self, id):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_READ_USER, (id,))
        data = cursor.fetchone()
        user = get_user_object(data) if data else None
        return user

    def search_by_login(self, login):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_READ_USER_LOGIN, (login,))
        data = cursor.fetchone()
        user = get_user_object(data) if data else None
        return user

    def get_user_id(self,login):
        cursor = self.__db.connection.cursor()
        cursor.execute(SQL_SEARCH_USER, (login,))
        fields = cursor.fetchone()
        return fields[0] if fields else None

    def delete(self, id):
        self.__db.connection.cursor().execute(SQL_DELETE_USER, (id,))
        self.__db.connection.commit()

