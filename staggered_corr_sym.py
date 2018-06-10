import pandas

def get_s_n_p_symbols():
        ticker_frame = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", header=0)[0]
        return list(ticker_frame['Ticker symbol'])

def extract_prices(symbols, months, end_date = None):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import quandl
    quandl.ApiConfig.api_key = 'tsx5KgftypGfsfs5shrt'

    if end_date is None:
        end_date = datetime.now() - relativedelta(months = 1)

    start_date = end_date - relativedelta(months = months)
    prices = pandas.DataFrame()
    for symbol in symbols:
        try :
            prices[symbol] = quandl.get("WIKI/{}".format(symbol), 
                                start_date=start_date.strftime('%Y-%m-%d'), 
                                end_date=end_date.strftime('%Y-%m-%d'), 
                                collapse='monthly')['Close']
        except Exception:
            print("Could not retrieve data for {}".format(symbol))
        

    return prices

def compute_staggered_corr(prices, prime_symbol, staggered_symbol, stagger):
    import numpy
    from collections import namedtuple
    StaggeredCorr = namedtuple('StaggeredCorr', ['prime_symbol', 'staggered_symbol', 'correlation'])

    staggered_start = prices.index[stagger]
    staggered_end = prices.index[-1 - stagger]
    correlation = numpy.corrcoef(prices.loc[staggered_start:, prime_symbol], prices.loc[:staggered_end, staggered_symbol])[1][0]
    return StaggeredCorr(prime_symbol, staggered_symbol, correlation)

def gen_staggered_corrs(prices, symbols, stagger):
    return (compute_staggered_corr(prices, ps, ss, stagger) for ps in symbols for ss in symbols)

def get_top_corrs(prices, symbols, amount = 5, stagger = 1):
    top_corrs = []
    i = 0
    staggered_corrs = [sc for sc in gen_staggered_corrs(prices, symbols, stagger) if not pandas.isnull(sc.correlation)]
    staggered_corrs = sorted(staggered_corrs, key = lambda x : abs(x.correlation), reverse = True)
    while len(top_corrs) < amount and i < len(staggered_corrs):
        if staggered_corrs[i].prime_symbol not in [tc.prime_symbol for tc in top_corrs]:
            top_corrs.append(staggered_corrs[i])
        i += 1

    return top_corrs

def get_predicted_direction(prices, stagger, staggered_corrs):
    staggered_symbols = list(set([s.staggered_symbol for s in staggered_corrs]))
    staggered_deltas = prices[staggered_symbols][-stagger-2:-stagger].diff().tail(1).reset_index(drop=True).transpose()[0]
    staggerd_direction = staggered_deltas.apply(lambda x: 1 if x > 0 else -1).to_dict()
    return {s.prime_symbol: staggerd_direction[s.staggered_symbol] for s in staggered_corrs}

def rolling_prices(symbols, months, start_date, end_date):
    from dateutil.relativedelta import relativedelta

    current_date = start_date
    prices = extract_prices(symbols, months, current_date)

    while True:
        yield prices
        if current_date < end_date:
            current_date += relativedelta(months = 1)
            incr_prices = extract_prices(symbols, 1, current_date)
            prices = pandas.concat([prices[1:], incr_prices.tail(1)])
        else:
            break

def long_bet(old_prc, new_prc):
    return new_prc - old_prc

def short_bet(old_prc, new_prc):
    return old_prc - new_prc

def place_bets(prices, predicted_direction, staggered_corrs):
    from functools import partial

    # long_bet = lambda old_prc, new_prc : new_prc - old_prc
    # short_bet = lambda old_prc, new_prc : old_prc - new_prc
    latest_prices = prices.tail(1).squeeze().to_dict()
    bets = {}
    for sc in staggered_corrs:
        direction = predicted_direction[sc.prime_symbol]
        if (direction > 0 and sc.correlation > 0) or (direction <= 0 and sc.correlation <= 0):
            bets[sc.prime_symbol] = partial(long_bet, latest_prices[sc.prime_symbol])
        elif (direction <= 0 and sc.correlation > 0) or (direction > 0 and sc.correlation <= 0):
            bets[sc.prime_symbol] = partial(short_bet, latest_prices[sc.prime_symbol])

    return bets

def calc_new_totals(prices, prev_bets, prev_totals):
    latest_prices = prices.tail(1).squeeze().to_dict()
    new_totals = prev_totals.copy()
    for symbol, bet in prev_bets.items():
        outcome = bet(latest_prices[symbol])
        if symbol in new_totals:
            new_totals[symbol] += outcome
        else:
            new_totals[symbol] = outcome

    return new_totals

if __name__ == '__main__':
    from datetime import datetime

    # symbols = ['NRG', 'VRTX', 'BA', 'CNC', 'RHT', 'CAT', 'ADBE', 'MAR']
    # symbols = ['NRG', 'VRTX', 'BA', 'CNC', 'RHT']
    symbols = get_s_n_p_symbols()[:50]
    start_date = datetime(2017, 9, 30)
    end_date = datetime(2018, 2, 28)
    instance = 1
    stagger = 1
    totals = {}
    bets = {}
    for prices in rolling_prices(symbols, 24, start_date, end_date):
        totals = calc_new_totals(prices, bets, totals)
        staggered_corrs = get_top_corrs(prices, symbols, 3, stagger)
        predicted_directions = get_predicted_direction(prices, stagger, staggered_corrs)
        bets = place_bets(prices, predicted_directions, staggered_corrs)
        
        prev_prcs = prices[-2:-1].squeeze().to_dict()
        curr_prcs = prices[-1:].squeeze().to_dict()

        print("\n\nProcess Details")
        for sc in staggered_corrs:
            
            output = "Symbol: {0}, Prev Price:{1}, Current Price:{2}, Predicted Direction:{3}, Correlation:{4}, Bet:{5}, Gross:{6}"
            print(output.format(sc.prime_symbol,
                                prev_prcs[sc.prime_symbol],
                                curr_prcs[sc.prime_symbol],
                                predicted_directions[sc.prime_symbol],
                                sc.correlation,
                                bets[sc.prime_symbol].func.__name__,
                                totals.get(sc.prime_symbol, None)))

        # print("\n\nCorrelations")
        # for sc in staggered_corrs:
        #     print("{0} : {1} => {2}, {3}".format(sc.prime_symbol, sc.staggered_symbol, sc.correlation, prices.tail(1)[sc.prime_symbol][0]))

    print("\n\nTotals")
    for i, x in totals.items():
        print("{0} => {1}".format(i, x))
        
        
        

    