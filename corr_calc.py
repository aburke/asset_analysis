""" Calculate correlations between stocks """
import numpy
from stock_sourcer import StockSourcer
from threading import Thread

class CorrCalcThread(Thread):
    
    def __init__(self, prcs_df, symbol, compare_syms, stagger, threshold):
        super(CorrCalcThread, self).__init__()
        self.prcs_df = prcs_df
        self.symbol = symbol
        self.compare_syms = compare_syms
        self.stagger = stagger
        self.threshold = threshold

    def run(self):
        staggerd_corrs = CorrAnalysis.calc_staggered_corr(self.prcs_df, self.symbol, self.compare_syms, self.stagger, self.threshold)
        for i,x in staggerd_corrs.items():
            print("({sym}, {compare_sym}[staggered]) => {corr}".format(sym = self.symbol, compare_sym = i, corr = x))
    

class CorrAnalysis(object):
    
    sym_sources = {'SNP' : StockSourcer.get_s_n_p_symbols_alpha,
                    'SAMPLE' : lambda : ['NRG', 'VRTX', 'BA', 'CNC', 'RHT', 'CAT', 'ADBE', 'MAR']}
    
    def __init__(self, symbol_source):
        self.symbol_univ = self.sym_sources[symbol_source]()

    def get_corr_symbols(self, num_years, stagger, threshold):
        prcs_df = StockSourcer.extract_prices(self.symbol_univ, num_years)
        for symbol in self.symbol_univ:
            corr_thread = CorrCalcThread(prcs_df, symbol, self.symbol_univ, stagger, threshold)
            corr_thread.setName("{} Correlation Thread".format(symbol))
            corr_thread.start()
            corr_thread.join()

    @staticmethod
    def calc_staggered_corr(prcs_df, symbol, compare_symns, stagger, threshold):
        staggerd_start = prcs_df.index[stagger]
        staggerd_end = prcs_df.index[-1 - stagger]
        s_corrs = {}
        for sym in compare_symns:
            s_corr = numpy.corrcoef(prcs_df.loc[staggerd_start:,symbol], prcs_df.loc[:staggerd_end, sym])[1][0]
            if threshold <= abs(s_corr):
                s_corrs[sym] = s_corr
        return s_corrs

