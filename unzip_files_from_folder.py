# coding: utf-8
import os
from zipfile import ZipFile

def unzip_files_from_folder(folder_zip='contracts/zip_files/', folder_unzip='contracts/unzip_files/'):
    for file in os.listdir(folder_zip):
        zip_filename = folder_zip + file
        with ZipFile(zip_filename, 'r') as zip_obj:
            file_names = zip_obj.namelist()
            for file_name in file_names:
                if file_name.endswith('.xml') and 'contract_' in file_name:
                    if os.path.exists(folder_unzip + file_name) is False:
                        zip_obj.extract(file_name, folder_unzip)
        print(file)
    return 0
    
    
if __name__ == '__main__':
    unzip_files_from_folder()
