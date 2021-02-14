from helpers import hashfile
from flask import  redirect,session,flash, url_for
from werkzeug.utils import secure_filename
from google.cloud import storage
from google.cloud import datastore
import os
from config import UPLOAD_PATH, BUCKET_NAME

storage_client = storage.Client()
datastore_client = datastore.Client()


def create_storage_file(file,user_id):
    file_name = file.filename.lower()

    if not file_name.endswith(('.png', '.jpeg', '.pdf', '.txt', '.docx')): 
        flash('Arquivo inválido')
        return redirect(url_for('user_screen'))
    
    file_name = secure_filename(file_name)
    key = f'user-{user_id}/{file_name}'

   # Pra mandar um arquivo pro storage, tem que salvar ele local primeiro
    tmp_file_path = os.path.join(UPLOAD_PATH,file.filename)
    file.save(tmp_file_path)

    # Salvando no Storage
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = storage.Blob(key, bucket)
    blob.upload_from_filename(tmp_file_path)

    blob.make_public()
    file_url = blob.public_url

    # Pegando o Hash
    with open(tmp_file_path,'rb') as f:
        uploaded_file_hash = hashfile(f.read())
    os.remove(tmp_file_path)

    return (file_url,uploaded_file_hash)
