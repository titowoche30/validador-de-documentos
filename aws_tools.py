from config import BUCKET_NAME, S3_KEY, S3_SECRET, S3_SESSION, UPLOAD_PATH
from helpers import hashfile
import boto3 
from botocore.config import Config
from boto3.dynamodb.conditions import Attr
from flask import  redirect,session,flash, url_for, send_from_directory
from werkzeug.utils import secure_filename
import time
import datetime
import simplejson as json
import pandas as pd


s3 = boto3.client("s3",
   aws_access_key_id = S3_KEY,
   aws_secret_access_key = S3_SECRET,
   aws_session_token = S3_SESSION)

s3_resource = boto3.resource('s3',
   aws_access_key_id = S3_KEY,
   aws_secret_access_key = S3_SECRET,
   aws_session_token = S3_SESSION)


my_config = Config(
    region_name = 'us-east-1'
)

dynamodb = boto3.resource('dynamodb',config=my_config,
   aws_access_key_id = S3_KEY,
   aws_secret_access_key = S3_SECRET,
   aws_session_token = S3_SESSION)

table = dynamodb.Table('Validation')

def upload_file_to_s3(file,file_name, bucket_name, acl="public-read"):
    try:
        s3.upload_fileobj(file, bucket_name, file_name,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e


def create_s3_file(file,user_id):
    file_name = file.filename.lower()

    if not file_name.endswith(('.png', '.jpeg', '.pdf')): 
        flash('Arquivo inválido')
        return redirect(url_for('user_screen'))

    
    file_name = secure_filename(file_name)
    timestamp = time.time()
    key = f'user-{user_id}/{timestamp}--{file_name}'

    if(isinstance(upload_file_to_s3(file,key,BUCKET_NAME),Exception)):
        flash("Upload não efetuado")
        return redirect(url_for('user_screen'))

    s3_file = s3.get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read()
    hash = hashfile(s3_file)

    file_adress = f'https://{BUCKET_NAME}.s3.amazonaws.com/{key}'
     
    
    return (user_id,file_adress,hash)

def delete_s3_file(file_adress,file_id):
    aux = len(f'https://{BUCKET_NAME}.s3.amazonaws.com/')
    file = file_adress[aux:]

    delete_response = s3.delete_object(Bucket=BUCKET_NAME,Key=file)
    if isinstance(delete_response,Exception):
        flash("Erro na remoção do arquivo efetuado")
        return redirect(url_for('user_screen'))

    return file_id

def delete_s3_user_folder(user_id):
    try:
        bucket = s3_resource.Bucket(BUCKET_NAME)
        bucket.objects.filter(Prefix=f'user-{user_id}/').delete()
    except Exception as e:
        flash('Erro em deletar o folder do user')
        return e

def write_to_dynamo(file_id,motive,pos_val_flag,neg_val_flag):
    hour = f'{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}'

    with table.batch_writer() as batch:
        batch.put_item(
               Item={
                   'id': int(time.time()),
                   'data': datetime.date.today().strftime("%d/%m/%Y"),
                   'fileid': file_id,
                   'hora': hour,
                   'motivation': motive,
                   'pos_val': pos_val_flag,
                   'neg_val': neg_val_flag
                   }
                )

def delete_file_from_dynamo(id):
    response = table.scan(FilterExpression=Attr('fileid').eq(f'{id}'))

    for response in response['Items']:
        key = response['id']
        table.delete_item(
            Key={
                'id': key,
            }
        )

def generate_log(file):
    response = table.scan(
    FilterExpression=Attr('fileid').eq(f'{file.id}')
)
 
    items = response['Items']
    if not items:
        return None
        
    with open(f'{UPLOAD_PATH}/log.json', 'w') as json_file:
        json.dump(items, json_file, use_decimal=True)

    log_df = pd.read_json(f'{UPLOAD_PATH}/log.json')
    log_df.drop(['id','fileid'],axis=1,inplace=True)
    log_df.to_csv(f'{UPLOAD_PATH}/log.csv',index=False)

    return True

def set_files_val(files):
    for file in files:
        response = table.scan(FilterExpression=Attr('fileid').eq(f'{file.id}'))

        for response in response['Items']:
            file.pos_val += response['pos_val']
            file.neg_val += response['neg_val']  

    return files
