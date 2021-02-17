import math
from scipy.stats import norm
from datetime import date
import numpy as np


class Option:
    """
    This class will group the different black-shcoles calculations for an opion
    """
    def __init__(self, cp, s, k,  t, vol, rf = 0.01, div = 0):
        self.cp = cp # 'C' or 'P'
        self.k = float(k) #strike
        self.s = float(s) #spot
        self.t = float(t) # time to expiration
        self.rf = float(rf) # risk free rate
        self.vol = float(vol) # volatility
        self.div = float(div) # dividend %

 
    def get_price(self):
        d1 = ( math.log(self.s/self.k) + ( self.rf + self.div + math.pow( self.vol, 2)/2 ) * self.t ) / ( self.vol * math.sqrt(self.t) )
        d2 = d1 - self.vol * math.sqrt(self.t)
        if self.cp == 'C':
            return ( norm.cdf(d1) * self.s * math.exp(-self.div*self.t) - norm.cdf(d2) * self.k * math.exp( -self.rf * self.t ) )
            # self.delta = norm.cdf(d1)
        elif self.cp == 'P':
            return  ( -norm.cdf(-d1) * self.s * math.exp(-self.div*self.t) + norm.cdf(-d2) * self.k * math.exp( -self.rf * self.t ) )
            # self.delta = -norm.cdf(-d1) 
 
    
    def get_delta(self, s_bump = .01):
        p = self.get_price()
        self.s += s_bump
        l = self.get_price()
        self.s -= s_bump
        return ((l-p)/s_bump)

    def get_rho(self, r_bump = .01):
        p = self.get_price()
        self.r += r_bump
        l = self.get_price()
        self.r -= r_bump
        return ((l-p)/r_bump)

    def get_vega(self, v_bump = 0.01):
        p = self.get_price()
        self.vol += v_bump
        l = self.get_price()
        self.vol -= v_bump
        return ((l-p)/v_bump)

    def get_theta(self, t_bump = 0.01):
        p = self.get_price()
        self.t -= t_bump
        l = self.get_price()
        self.t += t_bump
        return ((l-p)/t_bump)
 
    def get_gamma(self, s_bump = 0.01):
        p = self.get_delta()
        self.s += s_bump
        l = self.get_delta()
        self.s -= s_bump
        return (p - l) / s_bump

    def get_imp_vol(self, price):
        MAX_ITERATIONS = 200
        PRECISION = 0.00001
        vol = self.vol
        for i in range(MAX_ITERATIONS):
            calc_price = self.get_price()
            vega = self.get_vega()
            diff = price - calc_price
            if (abs(diff) < PRECISION):
                return vol
            vol = vol + diff/vega # f(x) / f'(x)
        return vol
 


if __name__ == '__main__':

    opt = Option("C", 794, 800, .25, .5)
    print(opt.get_price())
    print(opt.get_imp_vol(100))