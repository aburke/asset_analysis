""" Calculate correlations between stocks """
import numpy

class CorrCalc(object):

    def __init__(self, symbol):
        self.symbol = symbol

    def calc_staggerd_corr(self, symbols, range, stagger):
        pass