from io import BufferedRWPair
import mega_drive as md
import insta
from os.path import exists as file_exists
import os
import shutil
from datetime import datetime

loginCred = ['Ch_Insta_Cred.txt', 'Sp_Insta_Cred.txt']
insta_username_files = ['Ch.txt', 'Sp.txt']

for cred, u_names in zip(loginCred, insta_username_files):
    if file_exists('cache.txt'):
        os.remove('cache.txt')
        
    root_folder_name = f'{u_names[:2]}_{datetime.now().strftime("%d/%m/%Y %H:%M:%S").replace("/", "-")}'
    insta_login, insta_password = md.download_cred_file_extract(cred)
    insta.init(insta_login, insta_password)
    md.init_root_dir(root_folder_name)
    insta_usernames = md.download_insta_username_file_extract(u_names)
    for names in insta_usernames:
        try:
            insta.user_stories(names)
            if os.path.exists(names):
                md.upload_folder(root_folder_name, names)
        except Exception as e:
            print(e)