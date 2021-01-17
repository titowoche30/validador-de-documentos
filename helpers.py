import hashlib

def hashfile(file):
    sha256 = hashlib.sha256() 
    sha256.update(file) 
    return sha256.hexdigest()

