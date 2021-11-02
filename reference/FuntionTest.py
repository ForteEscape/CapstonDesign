import pandas
import pandas as pd
import pandas_datareader as pdr
from matplotlib import pyplot as plt
import os.path

class StockData:
    def __init__(self):
        self.__stock_type = {
            'kospi': 'stockMkt',
            'kosdaq': 'kosdaqMkt'
        }

    # 회사 이름을 이용하여 해당 회사의 주식 종목 코드를 받을 수 있는 함수
    def __getStockCode(self, dataFrame, name):
        code = dataFrame.query("name == '{}'".format(name))['code'].to_string(index=False)
        code = code.strip()
        return code

    # download url 조합
    def __getDownloadStock(self, market_type=None):
        market_type = self.__stock_type[market_type]
        download_link = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
        download_link = download_link + '?method=download'
        download_link = download_link + '&marketType=' + market_type

        dataframe = pd.read_html(download_link, header=0)[0]

        return dataframe

    def __getDownloadKospi(self):
        dataframe = self.__getDownloadStock('kospi')
        dataframe = dataframe.rename(columns={'회사명': 'name', '종목코드': 'code'})  # colum attribute 이름 수정

        dataframe.code = dataframe.code.map('{:06d}.KS'.format)

        return dataframe

    def __getDownloadKosdaq(self):
        dataframe = self.__getDownloadStock('kosdaq')
        dataframe = dataframe.rename(columns={'회사명': 'name', '종목코드': 'code'})  # colum attribute 이름 수정

        dataframe.code = dataframe.code.map('{:06d}.KQ'.format)

        return dataframe

    def getCompanyStockData(self, company_name):
        dataframe = pandas.read_csv('companylist.csv', delimiter=',')
        code = self.__getStockCode(dataframe, company_name)

        df = pdr.get_data_yahoo(code)

        return df

    def addCsvFile(self):
        if os.path.isfile('C:/Users/sehunKim/Desktop/Project/CapstonDesign/reference/companylist.csv'):
            print('companylist.csv already exists')
        else:
            kospi_dataframe = self.__getDownloadKospi()
            kosdaq_dataframe = self.__getDownloadKosdaq()

            code_dataframe = pd.concat([kospi_dataframe, kosdaq_dataframe])
            code_dataframe = code_dataframe[['name', 'code']]
            code_dataframe.to_csv('companylist.csv', encoding='utf-8-sig')


stockData = StockData()

stockData.addCsvFile()

data = stockData.getCompanyStockData('삼성전자')
data['Close'].plot()
plt.show()

# 입력 스트링
#company_input = input()
#data_start = input()
#data_end = input()

#code = getStockCode(code_dataframe, company_input)

# 해당 회사의 주가 데이터
#df = pdr.get_data_yahoo(code)

# graph 출력단
#df['Close'].plot()
#plt.show()