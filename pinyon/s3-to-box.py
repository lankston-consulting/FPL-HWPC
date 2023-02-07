# Python file to help build the webhook and get the folder id from box

from boxsdk import JWTAuth, Client
from typing import Mapping

config = JWTAuth.from_settings_file('config.json')
client = Client(config)


def get_folder():
    items = client.folder(folder_id='0').get_items()
    for item in items:
        print('{0} {1} is named "{2}"'.format(
            item.type.capitalize(), item.id, item.name))


get_folder()


# def create_webhook():

#     folder = client.folder(folder_id='192758983385')
#     webhook = client.create_webhook(folder, ['FILE.UPLOADED'], 'https://rsr547b8o5.execute-api.us-west-2.amazonaws.com/v1')
#     print('Webhook ID is {0}'.format(webhook.id))


# create_webhook()
