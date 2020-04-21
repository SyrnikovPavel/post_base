import pandas as pd
import datetime
import argparse
from tables import *

pd.options.display.float_format = '{:,.2f}'.format

def pro_contains(query, name_product):
    "Функция для отбора нужных позиций"
    if len(query.split(' ')) > 1:
        other_words = query.split(' ')[1:]
        for word in other_words:
            if word not in name_product:
                return False
        return True
    else:
        return True

parser = argparse.ArgumentParser(description='Поиск среди победителей тендеров')
parser.add_argument('-q', '--query',  action='store', dest='query', help='Поисковое слово')
args = parser.parse_args()


search_query = int(args.query)

data = [[
    x.name_product, 
    x.signDate, 
    x.sum_product,
    x.name,
    x.inn,
    x.email,
    x.phone,
] for x in Good.select().where(Good.inn == search_query)]

if data != []:

    df = pd.DataFrame(data, columns=[
        'name_product', 
        'signDate', 
        'sum_product',
        'name',
        'inn',
        'email',
        'phone',
    ])
    
    df['monthly'] = df.signDate.dt.to_period('M')
print("<" + "-"*60 + ">")  
print("Общая сумма выигранных закупок {0:,.2f}, количество выигранных закупок {1}".format(round(df['sum_product'].sum(),2), df['sum_product'].count()))
print("-"*60)
print("Топ 10 продаваемых товаров")
print(
    df.groupby(by=['name_product']).sum().sort_values(by=['sum_product'], ascending=False)[['sum_product']][:10]
)
print("-"*60)
print("Динамика за последние 10 активных месяцев")
print(
    df.groupby(by=['monthly']).sum()[['sum_product']][-10:]
)
