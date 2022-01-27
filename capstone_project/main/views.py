"""
본 기능이 구현되어 있는 main/views.py 파일입니다.

stock analysis의 경우 GRU model을 사용하여 이전 주식 데이터를 이용하여 이후 데이터를 예측합니다.
어떤 회사 주식을 예측하는지는 사용자의 input으로 들어오며 duration 역시 사용자 input으로 받습니다.

2022-01-08 20:20 - issue6에 추가된 개선사항 중 하나인 데이터 디렉토리 통일화 및 회사 이름 및 코드 csv 파일 갱신 로직 재구현
"""
import numpy as np
import plaidml.keras
from django.contrib.auth.decorators import login_required

plaidml.keras.install_backend()

from django.shortcuts import render
from .forms import *
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GRU
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import pandas_datareader as pdr
import os.path
import csv
from .stockdata import StockData


def index(request):
    return render(request, 'capstone_project/index.html')


@login_required(login_url='/accounts/login')
# Create your views here.
def stock_analysis(request):
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

    """
    company_list 데이터가 갱신될 때 마다 수정되도록 해 주어야 한다.
    
    사용자가 해당 view에 들어올때 data/company_list/companylist.csv의 신선도를 검사한다.
    만약 하루 정도의 차이가 난다면 자동으로 companylist.csv를 다시 만들어 갱신하도록 한다.
    
    => 신생 기업의 경우 주가 데이터가 없어 GRU기반 알고리즘이 제대로 동작하지 않을 가능성이 있다.
    따라서 매 분기(3달) 마다 companylist.csv를 갱신하도록 하는것이 더 좋을 것 같다.
    """
    
    # 만일 파일이 아예 존재하지 않을 경우에 데이터를 무조건 생성하도록 조치
    if not os.path.isfile('main/data/company_list/companylist.csv'):
        stock_manager = StockData()
        stock_manager.addCsvFile()

    # 매 분기 1일에 갱신을 진행한다.
    if today.month == 1 or 4 or 7 or 10 and today.day == 1:
        stock_data_manager = StockData()
        stock_data_manager.addCsvFile()

    # 이후 갱신된 파일 read
    path = 'main/data/company_list/companylist.csv'
    company_dataframe = pd.read_csv(path)

    if request.method == 'POST' and 'get-data' == request.POST.get('get-data'):
        form = Company(request.POST)

        if form.is_valid():
            company_name = form.cleaned_data['company_name_text']
            data_duration = form.cleaned_data['duration_option']
            stock_code = get_company_stock_code(company_dataframe, company_name)

            # 데이터 크롤링 기간 설정
            option = today - timedelta(int(data_duration))
            option_weight = 1
            data_duration_flag = False

            # 주가 정보 크롤링
            dataframe = pdr.get_data_yahoo(stock_code, '2014-01-01')
            dataframe['3MA'] = dataframe['Close'].rolling(window=3).mean()  # data moving average column
            dataframe['5MA'] = dataframe['Close'].rolling(window=5).mean()

            # 만약 해당 주가 정보 파일(csv)가 존재하지 않을 경우에 csv 파일 생성 및 저장 이후 해당 파일을 불러옴으로서 로딩 시간 단축
            stock_path = 'main/data/'
            if not os.path.isfile(stock_path + company_name + '.csv'):
                dataframe.to_csv(stock_path + company_name + '.csv', encoding='utf-8-sig')

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

            predict_dataframe = data_analysis(company_name, dataframe)
            data_inverse = dataframe.dropna()
            data_inverse = data_inverse[-100:]
            data_inverse_temp = date_list[-100:]
            adj_max = float(data_inverse['Close'].max())
            adj_min = float(data_inverse['Close'].min())

            predict_data_index = []
            for element in predict_dataframe:
                data_original = (float(element) * (adj_max - adj_min)) + adj_min  # 역 정규화
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

    return render(request, 'capstone_project/stock_analysis.html', {
        'form': form,
        'data': data,
        'label': date,
        'max': total_max + 1000,
        'min': total_min - 2000,
        'predict_data': predict_data,
        'predict_label': predict_date_list,
    })


def get_company_stock_code(dataframe, company_name):
    code = dataframe.query("name == '{}'".format(company_name))['code'].to_string(index=False)
    code = code.strip()
    return code


def data_analysis(company_name, dataframe):
    dataframe = dataframe.dropna()

    # data normalize
    scaler = MinMaxScaler()
    scale_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', '3MA', '5MA', 'Volume']
    scaled_dataframe = scaler.fit_transform(dataframe[scale_columns])
    scaled_dataframe = pd.DataFrame(scaled_dataframe, columns=scale_columns)

    feature_columns = ['3MA', '5MA', 'Close']
    label_columns = ['Close']

    label_dataframe = pd.DataFrame(scaled_dataframe, columns=label_columns)
    feature_dataframe = pd.DataFrame(scaled_dataframe, columns=feature_columns)

    label_numpy = label_dataframe.to_numpy()
    feature_numpy = feature_dataframe.to_numpy()

    window_size = 30

    X, Y = make_sequence_data(feature_numpy, label_numpy, window_size)

    split = -100 # data seperate

    x_train_data = X[0:split]
    y_train_data = Y[0:split]

    x_test_data = X[split:]
    y_test_data = Y[split:]

    model = Sequential()
    # 모델 구축
    model.add(GRU(
        256,
        activation='tanh',
        input_shape=x_train_data[0].shape
    ))

    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='adam', metrics=['mae'])
    early_stop_flag = EarlyStopping(monitor='val_loss', patience=5)
    model.fit(x_train_data, y_train_data, validation_data=(x_test_data, y_test_data),
              epochs=100, batch_size=16, callbacks=[early_stop_flag])

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