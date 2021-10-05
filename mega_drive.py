from mega import Mega
import json
import os
import shutil

json_object = json.load(open('mega_cred.json', 'r'))

mega = Mega()    
m = mega.login(json_object['email'],json_object['password'])
Insta_folder = m.find('Insta_Stories')
def upload(u_name):
    global m
    print(m.upload(f'./{u_name}.zip', Insta_folder[0]))
    os.remove(f'{u_name}.zip')

def get_insta_login():
    m.download_url('https://mega.nz/file/o5hEySgL#u4ufyqDHyn0osrJsyIcIPdjIYv2jsHLK9NkWV3s8tAQ')
    data = open('./Insta_Cred.txt','r').readlines()
    insta_username, insta_password = data[0].strip(), data[1].strip()
    os.remove("Insta_Cred.txt")
    return insta_username, insta_password

def get_insta_public_files():
    m.download_url('https://mega.nz/file/F9ZgXLRC#aCpZepKMfMMOC2UYI0ALRA_HDql5a9PIrYihVTOSmh0')
    data = open('./NoAccount.txt','r').readlines()
    stripped = [s.strip() for s in data]
    os.remove("NoAccount.txt")
    return stripped
