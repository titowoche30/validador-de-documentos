from config import BUCKET_NAME

class User:
    def __init__(self,name, login, password, email,id=None):
        self.name = name
        self.login = login
        self.password = password
        self.email = email
        self.id = id

    def __str__(self):
        return f'Nome: {self.name} login:{self.login} senha:{self.password} email: {self.email} id: {self.id}'

class File:
    def __init__(self, userid, file, hash, id = None, pos_val=0, neg_val=0):
        self.id = id
        self.userid = userid
        self.file = file
        self.hash = hash
        self.pos_val = pos_val
        self.neg_val = neg_val  

    def get_key(self):
        aux = len(f'https://{BUCKET_NAME}.s3.amazonaws.com/')
        return self.file[aux:].split('--')[1]


