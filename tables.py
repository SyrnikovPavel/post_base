# coding: utf-8

from peewee import *
from config import db_file

db = SqliteDatabase(db_file)


class Good(Model):
    unique_key = TextField(unique=True, verbose_name="Уникальный ключ")
    signDate = DateTimeField(verbose_name="Дата публикации")
    notificationNumber = TextField(unique=False, verbose_name="Номер извещения")
    name = TextField(unique=False, verbose_name="Наименование поставщика", index=True)
    inn = IntegerField(unique=False, verbose_name="ИНН Поставщика", index=True)
    kpp = IntegerField(unique=False, verbose_name="КПП Поставщика")
    address = TextField(unique=False, verbose_name="Адрес поставщика")
    phone = TextField(unique=False, verbose_name="Номер телефона поставщика")
    email = TextField(unique=False, verbose_name="Электронный адрес поставщика")
    name_product = TextField(unique=False, verbose_name="Наименование товара", index=True)
    OKPD2 = TextField(unique=False, verbose_name="Код ОКПД2")
    price_product = FloatField(unique=False, verbose_name="Цена товара")
    sum_product = FloatField(unique=False, verbose_name="Сумма товара")
    
    class Meta:
        database = db


class Archive(Model):
    name = TextField(unique=True, verbose_name="Наименование архива")
    download_bool = BooleanField(verbose_name="Скачивание")
    unzip_bool = BooleanField(verbose_name="Разархивирование")
    update_all_bool = BooleanField(verbose_name="Обновление")
    
    class Meta:
        database = db
        

db.create_tables([
    Good,
    Archive
])