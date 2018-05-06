"""Source stock data"""
import pandas
import quandl
quandl.ApiConfig.api_key = 'tsx5KgftypGfsfs5shrt'
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class StockSourcer(object):
    
    @staticmethod
    def get_s_n_p_symbols_alpha():
        return [x for x in StockSourcer.get_s_n_p_symbols() if x.isalpha()]
    
    @staticmethod
    def get_s_n_p_symbols():
        ticker_frame = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", header=0)[0]
        return list(ticker_frame['Ticker symbol'])

    @staticmethod
    def extract_prices(symbols, num_years):
        today = datetime.now() - relativedelta(months=1)
        prev_day = today - relativedelta(months=num_years*12)
        prices_df = pandas.DataFrame()
        for symbol in symbols:
            prices_df[symbol] = quandl.get("WIKI/{}".format(symbol), 
                                start_date=prev_day.strftime('%Y-%m-%d'), 
                                end_date=today.strftime('%Y-%m-%d'), 
                                collapse='monthly')['Close']

        return prices_df
