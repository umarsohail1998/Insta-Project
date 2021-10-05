import mega_drive as md
import insta

import os
import shutil
from datetime import datetime
import zipfile

local_folder = datetime.now().strftime("%d/%m/%Y %H:%M:%S").replace("/", "-")
os.mkdir(local_folder)
insta_username = md.get_insta_public_files()

for p_name in insta_username:
    insta.user_stories(p_name, local_folder)
    
zf = zipfile.ZipFile(f"{local_folder}.zip", "w")
for root, dirs, files in os.walk(local_folder):
    for file in files:
        zf.write(os.path.join(root, file))

shutil.rmtree(f'{local_folder}')
md.upload(local_folder)