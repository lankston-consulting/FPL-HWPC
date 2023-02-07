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

s = boto3.resource('s3')


def lambda_handler(event, context):

    if event and event['Records']:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            source_key = record['s3']['object']['key']
            big_bucket = s3_resource.Bucket(bucket)
            print(source_key)

            file_json = s3_resource.Object(bucket, source_key)

            data = file_json.get()['Body'].read().decode('utf-8')
            loader = json.loads(data)
            print(loader["project-name"])
            print(loader["run-name"])
            # hwpc-user-outputs/lambda-test-3-15-12-2022T23:59:27/results/1952_lambda-test-3.zip
            for objects in big_bucket.objects.filter(Prefix="hwpc-user-outputs/" + loader["project-name"] + "/"):
                print(objects.key)
                zip_item = s3_resource.Object(bucket, objects.key)

                with open('/tmp/file', 'w') as file1:
                    file1.write(data)

                newfile = client.folder(
                    folder_id='192758983385').upload('/tmp/file')


# def lambda_handler(event, context):
#     bucket = event['Records'][0]['s3']['bucket']['name']
#     key = event['Records'][0]['s3']['object']['key']

#     print(bucket)
#     print(key)
#     file = key.split('/')[-1]
#     print(file)
#     s3_object = s.Object(bucket, key)
#     data = s3_object.get()['Body'].read().decode('utf-8')
#     print(data)

#     with open('/tmp/'+file, 'w') as file1:
#         file1.write(data)

#     newfile = client.folder(folder_id='192758983385').upload('/tmp/'+file)

#     print("uploaded file: ", newfile)
