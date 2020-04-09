# coding: utf-8

from peewee import *
from config import db_file

db = SqliteDatabase(db_file)


class Good(Model):
    unique_key = TextField(unique=True, verbose_name="Уникальный ключ")
    notificationNumber = TextField(unique=False, verbose_name="Номер извещения")
    name = TextField(unique=False, verbose_name="Наименование поставщика")
    inn = IntegerField(unique=False, verbose_name="ИНН Поставщика")
    kpp = IntegerField(unique=False, verbose_name="КПП Поставщика")
    address = TextField(unique=False, verbose_name="Адрес поставщика")
    phone = TextField(unique=False, verbose_name="Номер телефона поставщика")
    email = TextField(unique=False, verbose_name="Электронный адрес поставщика")
    name_product = TextField(unique=False, verbose_name="Наименование товара")
    OKPD2 = TextField(unique=False, verbose_name="Код ОКПД2")
    price_product = FloatField(unique=False, verbose_name="Цена товара")
    sum_product = FloatField(unique=False, verbose_name="Сумма товара")
    
    class Meta:
        database = db


db.create_tables([
    Good,
])