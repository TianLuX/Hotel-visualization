import ast

import numpy as np
import json
from flask import Flask
from flask import render_template
import pymysql

con = pymysql.connect(host='localhost',
                      port=3306,
                      user='root',
                      password = 'xtl1536535935',
                      db='hotel-visualization')

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    # 不同国家酒店数量和星级均值
    location = []
    num = []  # 四星以上酒店的数量
    mean = []  # 酒店星级均值
    cur = con.cursor()
    sql = 'SELECT country,COUNT(country) as num,SUM(rating)/COUNT(country) as mean ' \
          'FROM hotels_features_dataset ' \
          'WHERE country IS NOT NULL AND rating IS NOT NULL GROUP BY country HAVING COUNT(country)>=600 ' \
          'ORDER BY COUNT(country) DESC'
    cur.execute(sql)
    data = cur.fetchall()

    for item in data:
        location.append(str(item[0]))
        num.append(item[1])
        mean.append(item[2])

    # 不同国家酒店均价
    sql = 'SELECT country, AVG(price) as price ' \
          'FROM hotels_features_dataset WHERE country IS NOT NULL AND price IS NOT NULL ' \
          'AND country IN (SELECT country FROM hotels_features_dataset ' \
          'WHERE country IS NOT NULL AND rating IS NOT NULL GROUP BY country HAVING COUNT(country)>=600)' \
          'GROUP BY country  ORDER BY price DESC'
    country = []
    price = []
    cur.execute(sql)
    data = cur.fetchall()

    for item in data:
        country.append(str(item[0]))
        price.append(float(item[1]))


    # 不同设施和星级
    facility = ['Wifi','Flatscreen TV','Non-smoking rooms','Air conditioning','Meeting rooms','Pool',
                'Baggage storage','Refrigerator']

    facilitysum = []
    facilityavg = []

    for i in range(np.array(facility).shape[0]):
        sql='SELECT COUNT(*) as sum,AVG(rating) FROM hotels_features_dataset ' \
            'WHERE rating IS NOT NULL AND rooms IS NOT NULL ' \
            'AND amenities IS NOT NULL AND (rooms LIKE \'%'+facility[i]+'%\' OR amenities LIKE \'%'+facility[i]+'%\')'
        cur.execute(sql)
        data = cur.fetchall()
        for item in data:
            facilitysum.append(item[0])
            facilityavg.append(item[1])

    # 不同类型房间占比
    room = ['City view','Smoking rooms available','Ocean view','Suites','Family rooms','Non-smoking rooms']
    areas = []
    datas = {}
    for i in range(np.array(room).shape[0]):
        sql='SELECT COUNT(*) FROM hotels_features_dataset WHERE rooms LIKE \'%'+room[i]+'%\' '
        cur.execute(sql)
        data_list = cur.fetchall()
        for item in data_list:
            datas[room[i]] = item[0]
            areas.append(item[0])

    #处理客户评论，客户评论是json数据
    rating = [1,2,3,4,5]
    evalution ={'Excellent':0,'Good':0,'Average':0,'Poor':0,'Terrible':0}
    fivestart=[]
    for i in rating:
        sql='SELECT reviews FROM hotels_features_dataset WHERE rating = %s and reviews NOT LIKE \'{}\''
        t = cur.execute(sql,i)
        data_list = cur.fetchall()
        for item in data_list:
            data = item[0]
            # 将JSON数据解码为dict（字典）
            data = ast.literal_eval(data)
            for key,value in data.items():
                if key in evalution:
                    evalution[key]+=value

        sum = 0
        mystar = []
        for key,value in data.items():
            sum+=value
        for key, value in data.items():
            mystar.append(value/sum)
        fivestart.append(mystar)


    cur.close()
    con.close()
    return render_template("index.html", location = location, num = num, mean = mean,
                           country = country,price=price,
                           facility = facility,facilitysum = facilitysum,facilityavg = facilityavg,
                           datas=datas, areas=areas,
                           fivestart = fivestart)


if __name__ == '__main__':
    app.run()
