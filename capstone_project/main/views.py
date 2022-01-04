import numpy as np
import plaidml.keras
from django.contrib.auth.decorators import login_required

plaidml.keras.install_backend()

from django.shortcuts import render
from .forms import *
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import pandas_datareader as pdr
import tensorflow as tf
import os.path
import csv

def index(request):
    return render(request, 'capstone_project/index.html')


# Create your views here.
@login_required(login_url='/accounts/login')
def stockanalysis(request):
    path = 'C:/Users/sehunKim/Desktop/Project/CapstonDesign/reference/companylist.csv'
    stock_path = 'C:/Users/sehunKim/Desktop/Project/CapstonDesign/capstone_project/main/data/'
    company_dataFrame = pd.read_csv(path)
    predict_data = []
    predict_date_list = []
    data = []
    date = []
    date_list = []
    total_min = 0
    total_max = 0
    predict_max = 0
    predict_min = 0
    today = datetime.today().date()
    company_name = ''
    data_duration = ''

    if request.method == 'POST' and 'get-data' == request.POST.get('get-data'):
        form = Company(request.POST)

        if form.is_valid():
            company_name = form.cleaned_data['company_name_text']
            data_duration = form.cleaned_data['duration_option']
            stock_code = getCompanyStockCode(company_dataFrame, company_name)

            # 데이터 크롤링 기간 설정
            option = today - timedelta(int(data_duration))
            option_weight = 1
            data_duration_flag = False

            # 주가 정보 크롤링
            dataFrame = pdr.get_data_yahoo(stock_code, '2014-01-01')
            dataFrame['3MA'] = dataFrame['Close'].rolling(window=3).mean() # data moving average column
            dataFrame['5MA'] = dataFrame['Close'].rolling(window=5).mean()

            # 만약 해당 주가 정보 파일(csv)가 존재하지 않을 경우에 csv 파일 생성 및 저장 이후 해당 파일을 불러옴으로서 로딩 시간 단축
            if not os.path.isfile(stock_path + company_name + '.csv'):
                dataFrame.to_csv(stock_path + company_name + '.csv', encoding='utf-8-sig')

            stock_file = open(stock_path + company_name + '.csv')
            stock_data = csv.reader(stock_file)

            for row in stock_data:
                date_list.append(row[0])

            stock_file.close()

            # 주식장이 주말 또는 공휴일일 경우를 대비한 날짜 수정
            while str(option) not in date_list:
                option = today - timedelta(int(data_duration) + option_weight)
                option_weight += 1

            stock_file = open(stock_path + company_name + '.csv')
            stock_data = csv.reader(stock_file)

            # 수정된 날자를 바탕으로 해당 날자부터 데이터를 저장
            for row in stock_data:
                if row[0] == str(option):
                    data_duration_flag = True

                if data_duration_flag:
                    data.append(row[4])
                    date.append(row[0])

            stock_file.close()

            data = list(map(float, data))
            data_max = max(data)
            data_min = min(data)

            predict_dataFrame = data_analysis(company_name, dataFrame)
            data_inverse = dataFrame.dropna()
            data_inverse = data_inverse[-100:]
            data_inverse_temp = date_list[-100:]
            adj_max = float(data_inverse['Close'].max())
            adj_min = float(data_inverse['Close'].min())

            predict_data_index = []
            for index in predict_dataFrame:
                data_original = (float(index) * (adj_max - adj_min)) + adj_min # 역 정규화
                predict_data_index.append(int(data_original))

            predict_date_temp = []
            for row in data_inverse_temp:
                predict_date_temp.append(row)

            data_append_flag = False
            for row in predict_date_temp:
                if row == str(option):
                    data_append_flag = True

                if data_append_flag:
                    predict_date_list.append(row)

            count = len(predict_date_list)
            predict_data = predict_data_index[-(count + 1):-1]
            predict_max = max(predict_data)
            predict_min = min(predict_data)

            total_max = data_max if data_max >= predict_max else predict_max
            total_min = data_min if data_min <= predict_min else predict_min
    else:
        form = Company()

    return render(request, 'capstone_project/stockanalysis.html', {
        'form': form,
        'data': data,
        'label': date,
        'max': total_max + 1000,
        'min': total_min - 2000,
        'predict_data': predict_data,
        'predict_label': predict_date_list,
    })

def getCompanyStockCode(dataframe, company_name):
    code = dataframe.query("name == '{}'".format(company_name))['code'].to_string(index=False)
    code = code.strip()
    return code

def data_analysis(company_name, dataFrame):
    dataFrame = dataFrame.dropna()

    # data normalize
    scaler = MinMaxScaler()
    scale_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', '3MA', '5MA', 'Volume']
    scaled_dataframe = scaler.fit_transform(dataFrame[scale_columns])
    scaled_dataframe = pd.DataFrame(scaled_dataframe, columns=scale_columns)

    feature_columns = ['3MA', '5MA', 'Close']
    label_columns = ['Close']

    label_dataframe = pd.DataFrame(scaled_dataframe, columns=label_columns)
    feature_dataframe = pd.DataFrame(scaled_dataframe, columns=feature_columns)

    label_numpy = label_dataframe.to_numpy()
    feature_numpy = feature_dataframe.to_numpy()

    window_size = 30

    X, Y = make_sequence_data(feature_numpy, label_numpy, window_size)

    split = -100 #data seperate

    x_train_data = X[0:split]
    y_train_data = Y[0:split]

    x_test_data = X[split:]
    y_test_data = Y[split:]

    model = Sequential()
    #모델 구축
    model.add(GRU(
        256,
        activation='tanh',
        input_shape=x_train_data[0].shape
    ))

    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='adam', metrics=['mae'])
    early_stop_flag = EarlyStopping(monitor='val_loss', patience=5)
    model.fit(x_train_data, y_train_data, validation_data=(x_test_data, y_test_data), epochs=100, batch_size=16, callbacks=[early_stop_flag])

    pred = model.predict(x_test_data)

    return pred

# make learning dataset
def make_sequence_data(feature_numpy, label_numpy, window_size):
    feature_list = []
    label_list = []

    for i in range(len(feature_numpy) - window_size):
        feature_list.append(feature_numpy[i: i + window_size])
        label_list.append(label_numpy[i + window_size])

    return np.array(feature_list), np.array(label_list)

