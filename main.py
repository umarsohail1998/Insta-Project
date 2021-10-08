import mega_drive as md
import insta

import os
import shutil
from datetime import datetime

# loginCred = ['Ch_Insta_Cred.txt','Mo_Insta_Cred.txt', 'Sp_Insta_Cred.txt']
# insta_username_files = ['Ch.txt', 'Mo.txt', 'Sp.txt']

loginCred = ['Ch_Insta_Cred.txt', 'Sp_Insta_Cred.txt']
insta_username_files = ['Ch.txt', 'Sp.txt']



for cred, u_names in zip(loginCred, insta_username_files):
    root_folder_name = f'{u_names[:2]}_{datetime.now().strftime("%d/%m/%Y %H:%M:%S").replace("/", "-")}'
    insta_login, insta_password = md.download_cred_file_extract(cred)
    insta.init(insta_login, insta_password)
    md.init_root_dir(root_folder_name)
    insta_usernames = md.download_insta_username_file_extract(u_names)
    for names in insta_usernames[:20]:
        insta.user_stories(names)
        if os.path.exists(names):
            md.upload_folder(root_folder_name, names)
    os.remove('cache.txt')
    # break



# local_folder = datetime.now().strftime("%d/%m/%Y %H:%M:%S").replace("/", "-")
# os.mkdir(local_folder)
# insta_username = md.get_insta_public_files()
# for p_name in insta_username[:5]:
#     insta.user_stories(p_name, local_folder)
  
# shutil.make_archive("Ch_"+local_folder,'zip',local_folder)  
# shutil.rmtree(f'{local_folder}')
# md.upload("Ch_"+local_folder)
