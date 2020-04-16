import pandas as pd
import datetime
import argparse
from tables import *

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
parser.add_argument('-cs', action='store', dest='c_sum', help='Коэффициент суммы', default=30)
parser.add_argument('-cd', action='store', dest='c_date', help='Коэффициент актуальности', default=70)
args = parser.parse_args()


c_sum = float(args.c_sum)
c_date = float(args.c_date)
query = args.query.lower()

total = c_sum + c_date

coef_sum = c_sum / total
coef_date = c_date / total


search_query = query.split(' ')[0]

data = [[
    x.name_product, 
    x.signDate, 
    x.sum_product,
    x.name,
    x.inn,
    x.email,
    x.phone,
] for x in Good.select().where(Good.name_product.contains(search_query)) if pro_contains(query, x.name_product)]

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

    sum_of_zak = df.groupby(by=['inn'])['sum_product'].sum()
    date_actual = datetime.datetime.today() - df.groupby(by=['inn'])['signDate'].max()

    rate_contractors = (sum_of_zak / sum_of_zak.max() * coef_sum + 1 / (date_actual / date_actual.min()) * coef_date).sort_values(ascending=False)

    print("Results:")
    for contractor in rate_contractors.index:
        emails = df[df.inn == contractor].email.unique()
        phones = df[df.inn == contractor].phone.unique()
        products = df[df.inn == contractor].name_product.unique()
        
        name = df[df.inn == contractor].name.values[0]
        email_str = ' '.join(emails)
        phone_str = ' '.join(phones)
        product_str = ' '.join(products)
        
        rate = round(rate_contractors[contractor] * 100, 2)
        
        print("="*110)
        print(
            name,
            contractor,
            email_str,
            phone_str,
            product_str,
            rate
        )
    