# coding: utf-8

from lxml import etree
from ftplib import FTP
from zipfile import ZipFile
from tables import *
import os
import datetime

def get_data_from_xml(file: str):
    "Функция принимает на вход xml файл и возвращает данные"

    with open(file, 'r', encoding="utf8") as fobj:
        xml = fobj.read()
        root = etree.fromstring(xml.encode('utf-8'))

    data = []
    
    if [protdate for protdate in root.iter('{http://zakupki.gov.ru/oos/types/1}protocolDate')] == []:

        signDate = datetime.datetime.strptime(str([x for x in root.iter('{http://zakupki.gov.ru/oos/types/1}signDate')][0].text)[:10], '%Y-%m-%d') 
        supplier = [suppliers for suppliers in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier')][0].find('{http://zakupki.gov.ru/oos/types/1}legalEntityRF')
        notificationNumber = str([x for x in root.iter('{http://zakupki.gov.ru/oos/types/1}id')][0].text)
        
        if supplier is not None:
            name = supplier.find('{http://zakupki.gov.ru/oos/types/1}fullName').text
            
        elif [suppliers for suppliers in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier')][0].find('{http://zakupki.gov.ru/oos/types/1}legalEntityForeignState') is not None:
            supplier = [suppliers for suppliers in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier')][0].find('{http://zakupki.gov.ru/oos/types/1}legalEntityForeignState')
            name = supplier.find('{http://zakupki.gov.ru/oos/types/1}fullName').text

        elif [suppliers for suppliers in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier')][0].find('{http://zakupki.gov.ru/oos/types/1}individualPersonRF') is not None:
            supplier = [suppliers for suppliers in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier')][0].find('{http://zakupki.gov.ru/oos/types/1}individualPersonRF')

            last_name = ''
            if supplier.find('{http://zakupki.gov.ru/oos/types/1}lastName') is not None:
                last_name = supplier.find('{http://zakupki.gov.ru/oos/types/1}lastName').text

            first_name = ''
            if supplier.find('{http://zakupki.gov.ru/oos/types/1}firstName') is not None:
                first_name = supplier.find('{http://zakupki.gov.ru/oos/types/1}firstName').text

            middle_name = ''
            if supplier.find('{http://zakupki.gov.ru/oos/types/1}middleName') is not None:
                middle_name = supplier.find('{http://zakupki.gov.ru/oos/types/1}middleName').text

            name = last_name + first_name + middle_name
        
        if supplier.find('{http://zakupki.gov.ru/oos/types/1}taxPayerCode') is not None:
            inn = int(supplier.find('{http://zakupki.gov.ru/oos/types/1}taxPayerCode').text)
        else:
            inn = int(supplier.find('{http://zakupki.gov.ru/oos/types/1}INN').text)
            
        kpp = int(0)
        if supplier.find('{http://zakupki.gov.ru/oos/types/1}KPP') is not None:
            kpp = int(supplier.find('{http://zakupki.gov.ru/oos/types/1}KPP').text)
          
        if supplier.find('{http://zakupki.gov.ru/oos/types/1}address') is not None:
            address = supplier.find('{http://zakupki.gov.ru/oos/types/1}address').text
        elif len([address for address in root.iter('{http://zakupki.gov.ru/oos/types/1}address')]) > 0:
            address = [address for address in root.iter('{http://zakupki.gov.ru/oos/types/1}address')][0]
        
        if supplier.find('{http://zakupki.gov.ru/oos/types/1}contactPhone') is not None:
            phone = supplier.find('{http://zakupki.gov.ru/oos/types/1}contactPhone').text
        elif len([phone for phone in root.iter('{http://zakupki.gov.ru/oos/types/1}contactPhone')]) > 0:
            phone = [phone for phone in root.iter('{http://zakupki.gov.ru/oos/types/1}contactPhone')][0]
        
        
        email = ''
        if supplier.find('{http://zakupki.gov.ru/oos/types/1}contactEMail') is not None:
            email = supplier.find('{http://zakupki.gov.ru/oos/types/1}contactEMail').text
        elif len([email for email in root.iter('{http://zakupki.gov.ru/oos/types/1}contactEMail')]) > 0:
            email =[email for email in root.iter('{http://zakupki.gov.ru/oos/types/1}contactEMail')][0]

        for product in root.iter('{http://zakupki.gov.ru/oos/types/1}product'):
            
            if product.find('{http://zakupki.gov.ru/oos/types/1}priceRUR') is not None:
                price_product = float(product.find('{http://zakupki.gov.ru/oos/types/1}priceRUR').text)
            else:
                price_product = float(product.find('{http://zakupki.gov.ru/oos/types/1}price').text)

            sum_product = price_product
            if product.find('{http://zakupki.gov.ru/oos/types/1}sumRUR') is not None:
                sum_product = float(product.find('{http://zakupki.gov.ru/oos/types/1}sumRUR').text)

            name_product = product.find('{http://zakupki.gov.ru/oos/types/1}name').text
            if product.find('{http://zakupki.gov.ru/oos/types/1}OKPD2') is not None:
                OKPD2 = product.find('{http://zakupki.gov.ru/oos/types/1}OKPD2').find('{http://zakupki.gov.ru/oos/types/1}code').text
            elif product.find('{http://zakupki.gov.ru/oos/types/1}KTRU') is not None:
                KTRU = product.find('{http://zakupki.gov.ru/oos/types/1}KTRU').find('{http://zakupki.gov.ru/oos/types/1}code').text
                OKPD2 = KTRU[:KTRU.find('-')]
            elif product.find('{http://zakupki.gov.ru/oos/types/1}OKPD') is not None:
                OKPD2 = product.find('{http://zakupki.gov.ru/oos/types/1}OKPD').find('{http://zakupki.gov.ru/oos/types/1}code').text

            unique_key = str(notificationNumber) + '_' + str(name_product) + '_' + str(sum_product)

            row = {
                'unique_key': unique_key,
                'signDate': signDate,
                'notificationNumber': notificationNumber,
                'name': name,
                'inn': inn,
                'kpp': kpp,
                'address': address,
                'phone': phone,
                'email': email,
                'name_product': name_product,
                'OKPD2': OKPD2,
                'price_product': price_product,
                'sum_product': sum_product,
            }
            data.append(row)
        
        return data
    
def get_files_from_zipfile(filename: str):
    "Фукнция возвращает список файлов в архиве"
    with ZipFile(filename, 'r') as zip_obj:
        file_names = zip_obj.namelist()
        return [file_name for file_name in file_names if ((file_name.endswith('.xml')) and ('contract_' in file_name))]

def unzip_files_from_folder(folder_zip='contracts/zip_files/', folder_unzip='contracts/unzip_files/'):
    'Функция для разархивации архивов'
    for file in os.listdir(folder_zip):
        zip_filename = folder_zip + file
        with ZipFile(zip_filename, 'r') as zip_obj:
            file_names = zip_obj.namelist()
            for file_name in file_names:
                if file_name.endswith('.xml') and 'contract_' in file_name:
                    if os.path.exists(folder_unzip + file_name) is False:
                        zip_obj.extract(file_name, folder_unzip)
    return 0
    
def unzip_file(filename, archive_name, folder_with_archives='contracts/zip_files/', folder_with_files = 'contracts/unzip_files2/'):
    'Функция для разархивации конкретного файла'
    zip_filename = folder_with_archives + archive_name
    with ZipFile(zip_filename, 'r') as zip_obj:
        if os.path.exists(folder_with_files + filename) is False:
            zip_obj.extract(filename, folder_with_files)
    return 0


def get_all_zip_files_from_ftp(host='ftp.zakupki.gov.ru', user='free', passwd='free', folder='/fcs_regions/Tjumenskaja_obl/contracts', outfolder='C:/projects/post_base/contracts/zip_files/'):
    "Функция для получения zip файлов из папки на ftp сервере"
    ftp = FTP(host=host)
    ftp.login(user=user, passwd=passwd)
    ftp.cwd(folder)
    return [file for file in ftp.nlst() if ((file[-4:]=='.zip') & ('2014' not in file))]


def update_zip_files_in_base(files: list):
    "Функция для обновления списка архивов"

    data_source = [{'name': file, 'download_bool': False, 'unzip_bool': False, 'update_all_bool': False} for file in files]
    with db.atomic():
        for batch in chunked(data_source, 20):
            Archive.insert_many(batch).on_conflict_ignore().execute()
            
    return 0


def download_zip_file_from_ftp(filename, host='ftp.zakupki.gov.ru', user='free', passwd='free', folder='/fcs_regions/Tjumenskaja_obl/contracts', outfolder='C:/projects/post_base/contracts/zip_files/'):
    "Функция для скачивания конкретного zip файла из папки на ftp сервере"
    
    ftp = FTP(host=host)
    ftp.login(user=user, passwd=passwd)
    ftp.cwd(folder)
    outfile = str(outfolder) + str(filename)
    if os.path.exists(outfile) is False:
        with open(outfile, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
    return 0

def download_all_zip_file_from_ftp(host='ftp.zakupki.gov.ru', user='free', passwd='free', folder='/fcs_regions/Tjumenskaja_obl/contracts', outfolder='C:/projects/post_base/contracts/zip_files/'):
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


def main():
    "Основной цикл программы"
    folder_ftp = '/fcs_regions/Tjumenskaja_obl/contracts'
    folder_with_archives = 'contracts/zip_files/'
    folder_with_files = 'contracts/unzip_files2/'


    # Обновление архивов
    files = get_all_zip_files_from_ftp()
    update_zip_files_in_base(files)

    not_update_arch = [archive for archive in Archive.select().where(Archive.update_all_bool == False)] # получаем не обновленные архивы

    for archive in not_update_arch:
        # проверка на скачивание
        if os.path.exists(folder_with_archives + archive.name) is not True:
            download_zip_file_from_ftp(archive.name, folder=folder_ftp) # скачиваем архив
            archive.download_bool=True
            archive.save()

        files_in_archive = get_files_from_zipfile(folder_with_archives + str(archive.name)) # файлы в архиве
        files_in_folder = os.listdir(folder_with_files) # файлы в папке

        # проверка на полную разархивацию
        for file in files_in_archive:
            if file not in files_in_folder:
                unzip_file(file, archive.name) # разархивируем файл, если еще не сделали это

        archive.unzip_bool=True
        archive.save()

        # обновление данных из файлов
        data_source = []
        for file in files_in_archive:
            filename = folder_with_files + file
            new_data = get_data_from_xml(folder_with_files + file) # получаем данные из xml файла

            if new_data is not None:
                data_source += new_data # добавляем в массив, если в файле были данные

            # добавляем данные в базу
            if len(data_source) >= 300:
                with db.atomic():
                    for batch in chunked(data_source, 20):
                        Good.insert_many(batch).on_conflict_replace().execute()
                data_source = []
            os.remove(filename) # удаляем файл

        if data_source != []:
            with db.atomic():
                for batch in chunked(data_source, 20):
                    Good.insert_many(batch).on_conflict_replace().execute()

        archive.update_all_bool=True
        archive.save()

        os.remove(folder_with_archives + archive.name) # удаляем файл
        print(archive.name)
        
        
if __name__ == '__main__':
    main()