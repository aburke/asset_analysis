"""Run generic test scripts"""
import numpy
from datetime import datetime, timedelta
from stock_sourcer import StockSourcer
from dateutil.relativedelta import relativedelta
import quandl
from corr_calc import CorrAnalysis
quandl.ApiConfig.api_key = 'tsx5KgftypGfsfs5shrt'

if __name__ == '__main__':
    #print(numpy.corrcoef([0,1,2,3], [2,1,0,-2])[1][0])
    today = datetime.now() - relativedelta(months=1)
    prev_day = today - relativedelta(months=48)
    #df = StockSourcer.extract_prices(['MSFT'], prev_day.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
    #df = StockSourcer.extract_prices(['MSFT'], '2018-01-31', '2018-02-28')
    #print(today)
    #print(prev_day)
    #print(df['date'].unique())
    # data = quandl.get("WIKI/AAPL", 
    #                     start_date=prev_day.strftime('%Y-%m-%d'), 
    #                     end_date=today.strftime('%Y-%m-%d'), 
    #                     collapse='monthly')


    df = StockSourcer.extract_prices(['XOM', 'AAPL'], 2)
    stagger = 1
    start = df.index[stagger]
    end = df.index[-1 - stagger]
    # print(df.loc[start:,'XOM'])
    # print(df.loc[:end, 'AAPL'])
    #print(numpy.corrcoef(df.loc[start:,'XOM'], df.loc[:end, 'AAPL'])[1][0])
    ca = CorrAnalysis('SAMPLE')
    ca.get_corr_symbols(2, 1, 0.95)
    # for s in StockSourcer.get_s_n_p_symbols_alpha():
    #     print(s)

