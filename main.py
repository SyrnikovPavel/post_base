# coding: utf-8

from lxml import etree
from ftplib import FTP
from zipfile import ZipFile
from tables import *
import time
import traceback
import sys
import os
import datetime

def find_xml(search_string: str, root: etree._Element):
    "Фукнция для поиска элемента по его названию"
    anwser = [element for element in root.iter(search_string)]
    assert len(anwser) < 2, "Element must be unique"
    if len(anwser) == 1:
        return anwser[0]
    
def lfm_name(root: etree._Element):
    "Возвращает name для ИП"
    if root is not None:
        return root.text
    else:
        return ''
    
def find_supplier(root: etree._Element):
    "Функция возвращает продавца"
    supplier = find_xml('{http://zakupki.gov.ru/oos/types/1}supplier', root)
    if find_xml('{http://zakupki.gov.ru/oos/types/1}legalEntityRF', supplier) is not None:
        supplier = find_xml('{http://zakupki.gov.ru/oos/types/1}legalEntityRF', supplier)
    elif find_xml('{http://zakupki.gov.ru/oos/types/1}legalEntityForeignState', supplier) is not None:
        supplier = find_xml('{http://zakupki.gov.ru/oos/types/1}legalEntityForeignState', supplier)
    elif find_xml('{http://zakupki.gov.ru/oos/types/1}individualPersonRF', supplier) is not None:
        supplier = find_xml('{http://zakupki.gov.ru/oos/types/1}individualPersonRF', supplier)
    elif find_xml('{http://zakupki.gov.ru/oos/types/1}individualPersonForeignState', supplier) is not None:
        supplier = find_xml('{http://zakupki.gov.ru/oos/types/1}individualPersonForeignState', supplier)   
        
    return supplier

def find_name(supplier: etree._Element):
    "Функция возвращает название организации"
    name = ''
    if find_xml('{http://zakupki.gov.ru/oos/types/1}fullName', supplier) is not None:
        name = find_xml('{http://zakupki.gov.ru/oos/types/1}fullName', supplier).text
    else:
        last_name = lfm_name(find_xml('{http://zakupki.gov.ru/oos/types/1}lastName', supplier))
        first_name = lfm_name(find_xml('{http://zakupki.gov.ru/oos/types/1}firstName', supplier))
        middle_name = lfm_name(find_xml('{http://zakupki.gov.ru/oos/types/1}middleName', supplier))

        name = last_name + ' ' + first_name + ' ' + middle_name
    
    return name

def find_inn(supplier: etree._Element):
    "Возвращает ИНН"
    inn = int(0)
    if find_xml('{http://zakupki.gov.ru/oos/types/1}taxPayerCode', supplier) is not None:
        raw_inn = find_xml('{http://zakupki.gov.ru/oos/types/1}taxPayerCode', supplier).text.replace(' ', '')
        if raw_inn.isdigit():
            inn = int(raw_inn)
    elif find_xml('{http://zakupki.gov.ru/oos/types/1}INN', supplier) is not None:
        raw_inn = find_xml('{http://zakupki.gov.ru/oos/types/1}INN', supplier).text.replace(' ', '')
        if raw_inn.isdigit():
            inn = int(raw_inn)
    return inn

def find_kpp(supplier: etree._Element):
    "Функция возвращает КПП"
    kpp = int(0)
    if find_xml('{http://zakupki.gov.ru/oos/types/1}KPP', supplier) is not None:
        raw_kpp = find_xml('{http://zakupki.gov.ru/oos/types/1}KPP', supplier).text.replace(' ', '')
        if raw_kpp.isdigit():
            kpp = int(raw_kpp)
    return kpp

def find_string(string: str, supplier: etree._Element):
    "Функция ведет поиск и возращает пустую строку есть нет результата"
    answer = ''
    if find_xml(string, supplier) is not None:
        answer = find_xml(string, supplier).text
    return answer

def find_address(supplier: etree._Element):
    "Функция возвращает адрес"
    addresses = [element for element in supplier.iter('{http://zakupki.gov.ru/oos/types/1}address')]
    if len(addresses) == 0:
        address = ''
    else:
        address = addresses[0].text
    return address

def find_phone(supplier: etree._Element):
    "Функция возвращает телефон"
    phones = [element for element in supplier.iter('{http://zakupki.gov.ru/oos/types/1}contactPhone')]
    if len(phones) == 0:
        phone = ''
    else:
        phone = phones[0].text
    return phone

def find_email(supplier: etree._Element):
    "Функция возвращает емэйл"
    emails = [element for element in supplier.iter('{http://zakupki.gov.ru/oos/types/1}contactEMail')]
    if len(emails) == 0:
        email = ''
    else:
        email = emails[0].text.lower()
    return email

def find_date(root: etree._Element):
    "Функция возвращает дату документа"
    signDate = datetime.datetime.today()
    if find_xml('{http://zakupki.gov.ru/oos/types/1}protocolDate', root) is not None:
        signDate = datetime.datetime.strptime(str(find_xml('{http://zakupki.gov.ru/oos/types/1}protocolDate', root).text)[:10], '%Y-%m-%d') 
    else:
        signDate = datetime.datetime.strptime(str(find_xml('{http://zakupki.gov.ru/oos/types/1}signDate', root).text)[:10], '%Y-%m-%d') 
    return signDate

def find_price(product: etree._Element):
    "Функция возвращает цену товара"
    price_product = float(0)
    if find_xml('{http://zakupki.gov.ru/oos/types/1}priceRUR', product) is not None:
        price_product = float(find_xml('{http://zakupki.gov.ru/oos/types/1}priceRUR', product).text)
    else:
        price_product = float(find_xml('{http://zakupki.gov.ru/oos/types/1}price', product).text)
    return price_product

def find_OKPD2(product: etree._Element):
    "Функция возвращает код ОКПД2"
    OKPD2 = '99.00.10'
    if product.find('{http://zakupki.gov.ru/oos/types/1}OKPD2') is not None:
        OKPD2 = product.find('{http://zakupki.gov.ru/oos/types/1}OKPD2').find('{http://zakupki.gov.ru/oos/types/1}code').text
    elif product.find('{http://zakupki.gov.ru/oos/types/1}KTRU') is not None:
        KTRU = product.find('{http://zakupki.gov.ru/oos/types/1}KTRU').find('{http://zakupki.gov.ru/oos/types/1}code').text
        OKPD2 = KTRU[:KTRU.find('-')]
    elif product.find('{http://zakupki.gov.ru/oos/types/1}OKPD') is not None:
        OKPD2 = product.find('{http://zakupki.gov.ru/oos/types/1}OKPD').find('{http://zakupki.gov.ru/oos/types/1}code').text
    return OKPD2

def get_data_from_xml(file: str):
    "Функция принимает на вход xml файл и возвращает данные"

    with open(file, 'r', encoding="utf8") as fobj:
        xml = fobj.read()
        root = etree.fromstring(xml.encode('utf-8'))
    
    if len([element for element in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier')]) >= 1:
        
        data = []
        
        signDate = find_date(root)
        notificationNumber = str(find_xml('{http://zakupki.gov.ru/oos/types/1}id', root).text)
        
        if len([element for element in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier')]) == 1:
        
            supplier = find_supplier(root)
            name = find_name(supplier)
            inn = find_inn(supplier)
            kpp = find_kpp(supplier)
            address = find_address(supplier)
            phone = find_phone(supplier)
            email = find_email(supplier)

            
            for product in root.iter('{http://zakupki.gov.ru/oos/types/1}product'):
                
                price_product = find_price(product)

                sum_product = price_product
                if product.find('{http://zakupki.gov.ru/oos/types/1}sumRUR') is not None:
                    sum_product = float(product.find('{http://zakupki.gov.ru/oos/types/1}sumRUR').text)
                
                name_product = product.find('{http://zakupki.gov.ru/oos/types/1}name').text.lower().replace('\n', '')
                OKPD2 = find_OKPD2(product)
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
        
        else:
            for supp in root.iter('{http://zakupki.gov.ru/oos/types/1}supplier'):
                
                supplier = find_supplier(supp)
                name = find_name(supplier)
                inn = find_inn(supplier)
                kpp = find_kpp(supplier)
                address = find_address(supplier)
                phone = find_phone(supplier)
                email = find_email(supplier)

                
                for product in root.iter('{http://zakupki.gov.ru/oos/types/1}product'):
                    
                    price_product = find_price(product)

                    sum_product = price_product
                    if product.find('{http://zakupki.gov.ru/oos/types/1}sumRUR') is not None:
                        sum_product = float(product.find('{http://zakupki.gov.ru/oos/types/1}sumRUR').text)
                    
                    name_product = product.find('{http://zakupki.gov.ru/oos/types/1}name').text.lower().replace('\n', '')
                    OKPD2 = find_OKPD2(product)
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
    files = [file for file in ftp.nlst() if ((file[-4:]=='.zip') & ('2014' not in file))]
    ftp.quit()
    time.sleep(5)
    return files


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
    ftp.quit()
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


def main(folder_ftp='/fcs_regions/Tjumenskaja_obl/contracts'):
    "Основной цикл программы"
    
    folder_with_archives = 'contracts/zip_files/'
    folder_with_files = 'contracts/unzip_files2/'

    # Обновление архивов
    files = get_all_zip_files_from_ftp(folder=folder_ftp)
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
            try:
                new_data = get_data_from_xml(folder_with_files + file) # получаем данные из xml файла
            except:
                print(filename)
                traceback.print_exc()
                sys.exit()
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
    main(folder_ftp='/fcs_regions/Sverdlovskaja_obl/contracts')