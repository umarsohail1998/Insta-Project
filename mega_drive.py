from mega import Mega
import json
import os
import shutil

json_object = json.load(open('mega_cred.json', 'r'))

mega = Mega()
m = mega.login(json_object['email'],json_object['password'])
# Insta_folder = m.find('Insta_Stories')

def download(file_name):
    global m
    file = m.find(file_name)
    m.download(file)

def download_cred_file_extract(file_name):
    download(file_name)
    data = open(file_name,'r').readlines()
    insta_username, insta_password = data[0].strip(), data[1].strip()
    os.remove(file_name)
    return insta_username, insta_password

def download_insta_username_file_extract(file_name):
    download(file_name)
    data = open(file_name,'r').readlines()
    stripped = [s.strip() for s in data]
    os.remove(file_name)
    return stripped

def upload_folder(root_folder_name, user_name):
    global m
    m.create_folder(f'Insta_Stories/{root_folder_name}/{user_name}')
    folder = m.find(user_name)
    files_list = [f for f in os.listdir(user_name)]
    for x in files_list:
        print(x)
        m.upload(f'{user_name}/{x}', folder[0])
    shutil.rmtree(user_name)
