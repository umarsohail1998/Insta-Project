from mega import Mega
import json
import os
import time
import shutil

json_object = json.load(open('mega_cred.json', 'r'))

mega = Mega()
m = mega.login(json_object['email'],json_object['password'])
root_dir = 0

def init_root_dir(foldername):
    global m, root_dir
    root_dir = m.create_folder(f'Insta_Stories/{foldername}')

def download(file_name):
    global m
    file = m.find(file_name)
    m.download(file)

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
    # loc = f'Insta_Stories/{root_folder_name}/{user_name}'
    dirs = m.create_folder(user_name,root_dir[root_folder_name])
    # folder = m.find_path_descriptor(loc)
    # folder = m.find(loc, exclude_deleted=True)
    files_list = [f for f in os.listdir(user_name)]
    for x in files_list:
        tmp = f'{os.getcwd()}/{user_name}/{x}'
        m.upload(tmp, dirs[user_name])
    shutil.rmtree(user_name)

def print_details():
    global m
    tmp = m.find_path_descriptor('Insta_Storie')
    print(tmp)
    # for x in dir(m):
    #     print(x)
    # print(help(m.find_path_descriptor))
    # print(help(m.upload))
    # print(help(m.find))
    
# print_details()
# init_root_dir('Insta_Stories/Umar')