import boto3
import requests
import os
import boxsdk
from boxsdk import JWTAuth, Client
import json

# Initilize the box client
config = JWTAuth.from_settings_file('var/runtime/config.json')
client = Client(config)
box = boxsdk

s3 = boto3.resource('s3')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    print(bucket)
    print(key)
    file = key.split('/')[-1]
    print(file)
    obj = s3.Object(bucket, key)

    data = obj.get()['Body'].read()

    print(data)

    with open('/tmp/'+file, 'wb') as file1:
        file1.write(data)

    newfile = client.folder(folder_id='192758983385').upload('/tmp/'+file)

    print("uploaded file: ", newfile)
