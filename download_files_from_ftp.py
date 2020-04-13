# coding: utf-8

from ftplib import FTP
import os

def get_all_zip_files_from_ftp(host='ftp.zakupki.gov.ru', user='free', passwd='free', folder='/fcs_regions/Tjumenskaja_obl/contracts', outfolder='C:/projects/post_base/contracts/zip_files/'):
    "Функция для получения zip файлов из папки на ftp сервере"
    ftp = FTP(host=host)
    ftp.login(user=user, passwd=passwd)
    ftp.cwd(folder)
    return [file for file in ftp.nlst() if ((file[-4:]=='.zip') & ('2014' not in file))]

def download_zip_file_from_ftp(host='ftp.zakupki.gov.ru', user='free', passwd='free', folder='/fcs_regions/Tjumenskaja_obl/contracts', outfolder='C:/projects/post_base/contracts/zip_files/'):
    "Функция для скачивания zip файлов из папки на ftp сервере"
    ftp = FTP(host=host)
    ftp.login(user=user, passwd=passwd)
    ftp.cwd(folder)
    for file in ftp.nlst():
        if file[-4:]=='.zip':
            outfile = str(outfolder) + str(file)
            if os.path.exists(outfile) is False:
                with open(outfile, 'wb') as f:
                    ftp.retrbinary('RETR ' + file, f.write)
                    print(file)
    return 0
    
    
if __name__ == '__main__':
    download_zip_file_from_ftp(host='ftp.zakupki.gov.ru', user='free', passwd='free', folder='/fcs_regions/Tjumenskaja_obl/contracts', outfolder='C:/projects/post_base/contracts/zip_files/')
