from mega import Mega
import json
import os
import time
import shutil

json_object = json.load(open('mega_cred.json', 'r'))
mega = Mega()
m = mega.login(json_object['email'],json_object['password'])
root_dir = 'Insta_Stories'

def init_root_dir(foldername):
    global m, root_dir
    root_dir = m.create_folder(f'Insta_Stories/{foldername}')

def download(file_name):
    global m
    file = m.find(file_name)
    m.download(file, os.getcwd())

def download_cred_file_extract(file_name):
    download(file_name)
    data = open(f'{os.getcwd()}/{file_name}','r').readlines()
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
    global m,root_dir
    files_list = [f for f in os.listdir(user_name)]
    for x in files_list:
        tmp = f'{os.getcwd()}/{user_name}/{x}'
        m.upload(tmp, root_dir[root_folder_name])
    shutil.rmtree(user_name)

def print_details():
    global m
    tmp = m.find_path_descriptor('Insta_Stories')
    print(tmp)