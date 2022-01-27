"""
krx 사이트에서 주식 데이터를 받아 회사이름과 코드 데이터를 추출하여 관리하는 manager class 모듈

외부 public하게 노출된 메서드는 addCsvFile()과 getCompanyStockData() 이며 각 기능은 다음과 같다.

addCsvFile() : 해당 클래스에서 받아온 회사와 회사코드 데이터를 csv 파일로 지정된 경로에 저장
getCompanyData() : csv 파일을 읽은 뒤 회사 이름을 input으로 받아 해당 회사의 주식 코드를 return함
"""

import pandas
import pandas as pd
import pandas_datareader as pdr


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
        kospi_dataframe = self.__getDownloadKospi()
        kosdaq_dataframe = self.__getDownloadKosdaq()

        code_dataframe = pd.concat([kospi_dataframe, kosdaq_dataframe])
        code_dataframe = code_dataframe[['name', 'code']]
        code_dataframe.to_csv('main/data/company_list/companylist.csv', encoding='utf-8-sig')