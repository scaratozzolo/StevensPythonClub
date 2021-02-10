import pandas as pd
import numpy as np
import pandas_datareader as pdr
import yfinance as yf
yf.pdr_override()
from scipy import optimize
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta



class PortfolioOpt:

    def __init__(self, portfolio, start, end=None, lookahead=21, benchmark="^GSPC"):

        self.tickers = {}
        for k in portfolio:
            try:
                self.tickers[k] = yf.Ticker(k).info['shortName']
            except:
                self.tickers[k] = k
        # print(tickers_skipped)


        self.start = start
        if end is None:
            self.end = str(date.today() - timedelta(days=1))
        else:
            self.end = end

        self.lookahead = lookahead

        str_lengths = [len(f"{v} ({k}):") for k,v in self.tickers.items()]
        self.max_str = max(str_lengths) + 1

        self.all_data = pdr.get_data_yahoo(list(self.tickers.keys()), start=self.start, end=self.end)["Adj Close"]
        if self.lookahead:
            self.data = self.all_data.iloc[:-21]
            self.last_month = self.all_data.iloc[-21:]
        else:
            self.data = self.all_data
            self.last_month = None
        # self.ret = self.data.pct_change()

        self.ret = np.log(self.data/self.data.shift(1))

        self.benchmark = benchmark
        self.bench = pdr.get_data_yahoo(self.benchmark, start=self.start, end=self.end)["Adj Close"]
        # self.bench_ret = self.bench.pct_change()
        self.bench_ret = np.log(self.bench/self.bench.shift(1))
        self.bench_ret.rename(self.benchmark, axis=1, inplace=True)

        self.bench_er = round((self.bench_ret.mean() * 252),3)
        self.bench_vol = round((self.bench_ret.std() * np.sqrt(252)),3)
        self.bench_sharpe = round((self.bench_er/self.bench_vol),3)

        # print(self.bench_ret.sum(), np.exp(self.bench_ret.sum()) - 1)

    def refresh_data(self, start=None, end=None):

        if start is not None:
            self.start=start

        if end is not None:
            self.end=end
        else:
            self.end = str(date.today() - timedelta(days=1))

        self.data = pdr.get_data_yahoo(list(self.tickers.keys()), start=self.start, end=self.end)["Adj Close"]
        self.ret = np.log(self.data/self.data.shift(1))
        # self.ret = self.bench.pct_change()


        self.bench = pdr.get_data_yahoo(self.benchmark, start=self.start, end=self.end)["Adj Close"]
        # self.bench_ret = self.bench.pct_change()
        self.bench_ret = np.log(self.bench/self.bench.shift(1))
        self.bench_ret.rename(self.benchmark, axis=1, inplace=True)

        self.bench_er = round((self.bench_ret.mean() * 252),3)
        self.bench_vol = round((self.bench_ret.std() * np.sqrt(252)),3)
        self.bench_sharpe = round((self.bench_er/self.bench_vol),3)


    def _get_ret_vol_sr(self, weights):
        """
        Calculates the returns, volatility, and sharpe of a portfolio with given weights
        """
        weights = np.array(weights)
        ret = np.nansum(self.ret.mean() * weights) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(self.ret.cov()*252, weights)))
        sr = ret/vol
        return np.array([ret, vol, sr])

    def _neg_sharpe(self, weights):
        return self._get_ret_vol_sr(weights)[2] * -1

    def _neg_returns(self, weights):
        return self._get_ret_vol_sr(weights)[0] * -1

    def _minimize_volatility(self, weights):
        return self._get_ret_vol_sr(weights)[1]

    def _neg_beta(self, weights, beta_vec):
        return np.dot(beta_vec, x) * -1



    def optimize_portfolio(self, opt_for="sharpe", bounds=None, print_results=True, **kwargs):
        """
        Optimize portfolio buy maximizing sharpe, maximizing returns, or minimizing volatility
        """

        cons = ({'type':'eq', 'fun': lambda x: np.nansum(x)-1})
        if bounds is None:
            bounds = tuple((0,1) for _ in range(len(self.tickers)))
        init_guess = [1/len(self.tickers) for _ in range(len(self.tickers))]

        if opt_for == "sharpe":
            opt_results = optimize.minimize(self._neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "returns":
            opt_results = optimize.minimize(self._neg_returns, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "vol":
            opt_results = optimize.minimize(self._minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        else:
            raise ValueError(f"'opt_for' can only take the values 'sharpe', 'returns', or 'vol'")

        if print_results:

            self.print_results(opt_results, **kwargs)

        return opt_results


    def optimize_portfolio_returns(self, target_returns, opt_for="sharpe", bounds=None, print_results=True, **kwargs):
        """
        Optimize portfolio buy maximizing sharpe, maximizing returns, or minimizing volatility with a target return
        """

        cons = ({'type':'eq', 'fun': lambda x: np.nansum(x)-1},
                {'type':'eq', 'fun': lambda x: self._get_ret_vol_sr(x)[0] - target_returns})
        if bounds is None:
            bounds = tuple((0,1) for _ in range(len(self.tickers)))
        init_guess = [1/len(self.tickers) for _ in range(len(self.tickers))]

        if opt_for == "sharpe":
            opt_results = optimize.minimize(self._neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "returns":
            opt_results = optimize.minimize(self._neg_returns, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "vol":
            opt_results = optimize.minimize(self._minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        else:
            raise ValueError(f"'opt_for' can only take the values 'sharpe', 'returns', or 'vol'")

        if print_results:

            self.print_results(opt_results, **kwargs)

        return opt_results


    def optimize_portfolio_vol(self, target_vol, opt_for="sharpe", bounds=None, print_results=True, **kwargs):
        """
        Optimize portfolio buy maximizing sharpe, maximizing returns, or minimizing volatility with a target volatility
        """

        cons = ({'type':'eq', 'fun': lambda x: np.nansum(x)-1},
                {'type':'eq', 'fun': lambda x: self._get_ret_vol_sr(x)[1] - target_vol})
        if bounds is None:
            bounds = tuple((0,1) for _ in range(len(self.tickers)))
        init_guess = [1/len(self.tickers) for _ in range(len(self.tickers))]

        if opt_for == "sharpe":
            opt_results = optimize.minimize(self._neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "returns":
            opt_results = optimize.minimize(self._neg_returns, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "vol":
            opt_results = optimize.minimize(self._minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        else:
            raise ValueError(f"'opt_for' can only take the values 'sharpe', 'returns', or 'vol'")

        if print_results:

            self.print_results(opt_results, **kwargs)

        return opt_results

    def optimize_portfolio_beta(self, beta_target, opt_for="sharpe", bounds=None, print_results=True, **kwargs):
        """
        Optimize portfolio buy maximizing sharpe, maximizing returns, or minimizing volatility with a target beta with the benchmark
        """
        t = pd.concat([self.bench_ret, self.ret], axis=1)

        # Betas vector
        hist_covs = np.array(t.cov().iloc[0])
        bench_var = hist_covs[0]
        beta_vec = hist_covs[1:]/bench_var


        cons = ({'type':'eq', 'fun': lambda x: np.nansum(x)-1},
                {'type':'eq', 'fun': lambda x: np.dot(beta_vec, x)-beta_target})
        if bounds is None:
            bounds = tuple((0,1) for _ in range(len(self.tickers)))
        init_guess = [1/len(self.tickers) for _ in range(len(self.tickers))]

        if opt_for == "sharpe":
            opt_results = optimize.minimize(self._neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "returns":
            opt_results = optimize.minimize(self._neg_returns, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        elif opt_for == "vol":
            opt_results = optimize.minimize(self._minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        else:
            raise ValueError(f"'opt_for' can only take the values 'sharpe', 'returns', or 'vol'")

        if print_results:

            self.print_results(opt_results, beta_target=beta_target, **kwargs)

        return opt_results



    def amount_needed(self, opt_results):
        """
        Function to find the amount of money needed to created optimial portfolio
        """

        amount = 0

        if self.lookahead:
            last_price = self.last_month.iloc[-1].values
        else:
            last_price = self.data.iloc[-1].values

        for price, weight in zip(last_price, opt_results['x'].round(4)):

            if weight != 0:
                amount += price/weight

        return round(amount, 2)


    def calc_prev_month(self, opt_results):
        """
        Function to calculate the performance of the optimal weights over the previous month.
        """
        weights = opt_results['x'].round(3)

        daily_ret = np.log(self.last_month/self.last_month.shift(1))
        ret = np.nansum(daily_ret.sum() * weights)
        vol = np.sqrt(np.dot(weights.T, np.dot(daily_ret.cov(), weights)))
        sr = ret/vol

        return np.array([ret, vol, sr]).round(3)


    def print_results(self, opt_results, print_zeros=False, percentages=True, shares=True, dollars=True, amount_needed=True, amount=1000, beta_target=None):
        """
        A function to print the results of the optimization.
        """



        print(f"Data start:" + " "*(self.max_str-len("Data start:")) + f"{self.start}")
        print(f"Data end:" + " "*(self.max_str-len("Data end:")) + f"{self.end}\n")

        print("\nLookback Performance (Annualized)")
        print(f"Expected Returns:" + " "*(self.max_str-len("Expected Returns:")) + f"{round(self._get_ret_vol_sr(opt_results['x'])[0],3)}")
        print(f"Vol:" + " "*(self.max_str-len("Vol:")) + f"{round(self._get_ret_vol_sr(opt_results['x'])[1],3)}")
        print(f"Sharpe ratio:" + " "*(self.max_str-len("Sharpe ratio:")) + f"{round(self._get_ret_vol_sr(opt_results['x'])[2],3)}")
        if beta_target is not None:
            print(f"Beta Target:" + " "*(self.max_str-len("Beta Target:")) + f"{beta_target}")

        if self.lookahead:
            prev_month_data = self.calc_prev_month(opt_results)
            print(f"\nLookahead Performance: {self.lookahead} Days")
            print(f"Returns:" + " "*(self.max_str-len("Returns:")) + f"{prev_month_data[0]}")
            print(f"Vol:" + " "*(self.max_str-len("Vol:")) + f"{prev_month_data[1]}")
            print(f"Sharpe Ratio:" + " "*(self.max_str-len("Sharpe Ratio:")) + f"{prev_month_data[2]}")

        print(f"\nBenchmark ({self.benchmark})")
        print(f"Expected Returns:" + " "*(self.max_str-len("Expected Returns:")) + f"{self.bench_er}")
        print(f"Vol:" + " "*(self.max_str-len(f"Vol:")) + f"{self.bench_vol}")
        print(f"Sharpe ratio:" + " "*(self.max_str-len(f"Sharpe ratio:")) + f"{self.bench_sharpe}")
        print(f"Real returns:" + " "*(self.max_str-len("Real returns:")) + f"{(np.exp(self.bench_ret.sum()) - 1).round(3)}")
        print(f"Real Sharpe ratio:" + " "*(self.max_str-len("Real Sharpe ratio:")) + f"{((np.exp(self.bench_ret.sum()) - 1)/self.bench_vol).round(3)}")

        if percentages:
            print("\n" + "#"*(self.max_str+10))
            print("Optimal Percentages")
            for i, (k, v) in zip(opt_results['x'], self.tickers.items()):
                space = self.max_str - len(f"{v} ({k}):")

                value = round(i*100, 2)
                if value == 0 and not print_zeros:
                    continue

                print(f"{v} ({k}):" + " "*space + f"{value}")

        if shares:

            print("\n" + "#"*(self.max_str+10))
            print(f"Shares to buy (${amount})")
            dol_inv = (opt_results['x'] * amount).round(4)
            last_price = self.data.iloc[-1].values.round(2)
            shares = np.floor(dol_inv/last_price)

            for i, (k,v) in zip(shares, self.tickers.items()):
                space = self.max_str - len(f"{v} ({k}):")

                if i == 0 and not print_zeros:
                    continue

                print(f"{v} ({k}):" + " "*space + f"{i}")


        if dollars:

            print("\n" + "#"*(self.max_str+10))
            print(f"Dollars to buy (${amount})")
            dol_inv = opt_results['x'].round(4) * amount

            for i, (k,v) in zip(dol_inv.round(2), self.tickers.items()):
                space = self.max_str - len(f"{v} ({k}):")

                if i == 0 and not print_zeros:
                    continue

                print(f"{v} ({k}):" + " "*space + f"{i}")


        if amount_needed:

            print("\n" + "#"*(self.max_str+10))
            space = self.max_str - len("Amount needed:")
            print("Amount needed:" + " "*space + f"${self.amount_needed(opt_results)}")




    def save_results(self, file_name, opt_results, print_zeros=False, percentages=True, shares=True, dollars=True, amount_needed=True, amount=1000, beta_target=None):
        """
        A function to print the results of the optimization.
        """

        f = open(file_name, 'w')

        f.write(f"Data start:" + " "*(self.max_str-len("Data start:")) + f"{self.start}\n")
        f.write(f"Data end:" + " "*(self.max_str-len("Data end:")) + f"{self.end}\n")

        f.write("\nLookback Performance (Annualized)\n")
        f.write(f"Expected Returns:" + " "*(self.max_str-len("Expected Returns:")) + f"{round(self._get_ret_vol_sr(opt_results['x'])[0],3)}\n")
        f.write(f"Vol:" + " "*(self.max_str-len("Vol:")) + f"{round(self._get_ret_vol_sr(opt_results['x'])[1],3)}\n")
        f.write(f"Sharpe ratio:" + " "*(self.max_str-len("Sharpe ratio:")) + f"{round(self._get_ret_vol_sr(opt_results['x'])[2],3)}\n")
        if beta_target is not None:
            f.write(f"Beta Target:" + " "*(self.max_str-len("Beta Target:")) + f"{beta_target}\n")

        if self.lookahead:
            prev_month_data = self.calc_prev_month(opt_results)
            f.write(f"\nLookahead Performance: {self.lookahead} Days")
        f.write(f"Returns:" + " "*(self.max_str-len("Returns:")) + f"{prev_month_data[0]}")
        f.write(f"Vol:" + " "*(self.max_str-len("Vol:")) + f"{prev_month_data[1]}")
        f.write(f"Sharpe Ratio:" + " "*(self.max_str-len("Sharpe Ratio:")) + f"{prev_month_data[2]}")

        f.write(f"\nBenchmark ({self.benchmark})\n")
        f.write(f"Expected Returns:" + " "*(self.max_str-len("Expected Returns:")) + f"{self.bench_er}\n")
        f.write(f"Vol:" + " "*(self.max_str-len(f"Vol:")) + f"{self.bench_vol}\n")
        f.write(f"Sharpe ratio:" + " "*(self.max_str-len(f"Sharpe ratio:")) + f"{self.bench_sharpe}\n")
        f.write(f"Real returns:" + " "*(self.max_str-len("Real returns:")) + f"{(np.exp(self.bench_ret.sum()) - 1).round(3)}\n")
        f.write(f"Real Sharpe ratio:" + " "*(self.max_str-len("Real Sharpe ratio:")) + f"{((np.exp(self.bench_ret.sum()) - 1)/self.bench_vol).round(3)}\n")

        if percentages:
            f.write("\n" + "#"*(self.max_str+10) + "\n")
            f.write("Optimal Percentages\n")
            for i, (k, v) in zip(opt_results['x'], self.tickers.items()):
                space = self.max_str - len(f"{v} ({k}):")

                value = round(i*100, 2)
                if value == 0 and not print_zeros:
                    continue

                f.write(f"{v} ({k}):" + " "*space + f"{value}\n")

        if shares:

            f.write("\n" + "#"*(self.max_str+10) + "\n")
            f.write(f"Shares to buy (${amount})\n")
            dol_inv = opt_results['x'].round(4) * amount
            last_price = self.data.iloc[-1].values.round(2)
            shares = np.floor(dol_inv/last_price)

            for i, (k,v) in zip(shares, self.tickers.items()):
                space = self.max_str - len(f"{v} ({k}):")

                if i == 0 and not print_zeros:
                    continue

                f.write(f"{v} ({k}):" + " "*space + f"{i}\n")


        if dollars:

            f.write("\n" + "#"*(self.max_str+10) + "\n")
            f.write(f"Dollars to buy (${amount})\n")
            dol_inv = opt_results['x'].round(4) * amount

            for i, (k,v) in zip(dol_inv.round(2), self.tickers.items()):
                space = self.max_str - len(f"{v} ({k}):")

                if i == 0 and not print_zeros:
                    continue

                f.write(f"{v} ({k}):" + " "*space + f"{i}\n")


        if amount_needed:

            f.write("\n" + "#"*(self.max_str+10) + "\n")
            space = self.max_str - len("Amount needed:")
            f.write("Amount needed:" + " "*space + f"${self.amount_needed(opt_results)}\n")



if __name__ == "__main__":


    # tickers = ['XAR', 'KBE', 'XBI', 'KCE', 'XHE', 'XHS', 'XHB', 'KIE', 'XWEB', 'XME', 'XES', 'XOP', 'XPH', 'KRE', 'XRT', 'XSD', 'XSW', 'XTL', 'XTN']
    # tickers = ['XLC', 'XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLRE', 'XLK', 'XLU']

    tickers = ["RCL", "AAL", "MSFT", "BAC", "SNAP", "AMZN", "KO", "DIS", "COST", "VZ", "AMD", "NVDA", "WMT", "V", "HD", "DPZ", "JBLU", "MDLZ",
               "TSLA", "WEN", "UPS", "PLUG", "PLTR", "SNE"]
    
    # tickers = ["VOO", "IJH", "IJR", "IXUS"]
    # ssmif = pd.read_csv("ssmif_port.csv", header=None)
    # tickers = ssmif[0].values

    # spdr = pd.read_csv("spdr_holdings-all.csv")
    # tickers = spdr['Symbol'].unique()

    # watchlist = pd.read_csv("watchlist.csv", header=2)
    # tickers = watchlist['Symbol'].unique()

    # init_date = date(2019, 12, 20)
    # start_date = init_date - relativedelta(years=3)
    # opt = PortfolioOpt(tickers, start=str(start_date))
    # t = opt.optimize_portfolio(opt_for="sharpe", amount=1500)
    # # print(t)
    #
    # opt = PortfolioOpt(tickers, lookahead=0, start=start)
    # t = opt.optimize_portfolio(opt_for="sharpe", amount=1500)

    # try some backtesting

    init_date = date(2018, 12, 31)
    start_date = init_date - relativedelta(years=3)
    end_date = init_date
    # opt = PortfolioOpt(tickers, start=str(start_date), end=str(end_date))
    # t = opt.optimize_portfolio(opt_for="sharpe", amount=1500)
    port_val = 2000



    all_data = pdr.get_data_yahoo(tickers, start=init_date)["Adj Close"]

    # dol_inv = (t['x'] * port_val).round(2)
    # print(t['x'], dol_inv)
    # print(all_data.iloc[0])
    # print(all_data.iloc[0].values)
    # print(all_data.iloc[-1])
    # print(all_data.iloc[-1].values)
    # shares = np.floor(dol_inv/all_data.iloc[0].values)
    # port_val -= np.nansum(shares * all_data.iloc[0].values)
    # print(port_val)
    # port_val += np.nansum(shares * all_data.iloc[-1].values)
    # print(port_val)

    shares = np.zeros(len(tickers))

    for i, (date, row) in enumerate(all_data.iloc[1:].iterrows()):
        if date > end_date:
            print(port_val)
            last_price = row.values.round(2)
            port_val += np.nansum(shares * last_price)
            print(port_val, date)

            opt = PortfolioOpt(tickers, start=str(start_date), end=str(end_date), lookahead=0)
            t = opt.optimize_portfolio(opt_for="sharpe", amount=port_val, print_results=False)

            dol_inv = (t['x'] * port_val).round(2)
            # print(t['x'], dol_inv, last_price)
            # print(t['x'])
            # print(row)
            shares = np.floor(dol_inv/last_price)
            port_val -= np.nansum(shares * last_price)
            # print(start_date, end_date, date, last_price, dol_inv, shares)

            start_date = start_date + relativedelta(months=1)
            end_date = end_date + relativedelta(months=1)

    print(port_val)
    port_val += np.nansum(shares * all_data.iloc[-1].values)
    print(port_val)
