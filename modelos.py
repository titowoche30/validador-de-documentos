from config import BUCKET_NAME

class User:
    def __init__(self,name, login, password,telefone,email,id=None):
        self.name = name if len(name) <= 100 else None
        self.login = login if len(login) <= 20 else None
        self.password = password if len(password) <= 20 else None
        self.telefone = telefone if len(telefone) <= 20 else None
        self.email = email if len(email) <= 30 else None
        self.id = id 

    def valitade_fields(self):
        dict_fields = self.__dict__
        fields_size = {'name':100,'login':20,'password':20,'telefone':20,'email':30} 
        for key in dict_fields:
            if 'id' == key: continue 
            if dict_fields[key] is None:
                return f'O Campo {key} deve ter no máximo {fields_size[key]} caracteres'

        return False

    def __str__(self):
        return f'Nome: {self.name} login:{self.login} senha:{self.password} email: {self.email} id: {self.id}'

class File:
    def __init__(self, file, hash, userid,id = None):
        self.file = file
        self.hash = hash
        self.userid = userid
        self.id = id 

    def get_file_name(self):
        return self.file.split('/')[-1].split('.')[0]

    def get_file_extension(self):
        return self.file.split('.')[-1]

