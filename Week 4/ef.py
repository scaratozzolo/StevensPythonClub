import pandas as pd
import numpy as np
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import yfinance as yf
yf.pdr_override()


tickers = ["FB", "AAPL", "AMZN", "NFLX", "GOOG"]
stocks = pdr.get_data_yahoo(tickers, start="2017-01-01", end="2020-01-01")["Adj Close"]


log_ret = np.log(stocks/stocks.shift(1))

num_ports = 6000
all_weights = np.zeros((num_ports, len(stocks.columns)))
ret_arr = np.zeros(num_ports)
vol_arr = np.zeros(num_ports)
sharpe_arr = np.zeros(num_ports)

for x in range(num_ports):
    # Weights
    weights = np.array(np.random.random(len(stocks.columns)))
    weights = weights/np.sum(weights)

    # Save weights
    all_weights[x,:] = weights

    # Expected return
    ret_arr[x] = np.sum( (log_ret.mean() * weights)) * 252

    # Expected volatility
    vol_arr[x] = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov(), weights))) * np.sqrt(252)

    # Sharpe Ratio
    sharpe_arr[x] = ret_arr[x]/vol_arr[x]
#
# max_sr_ret = ret_arr[sharpe_arr.argmax()]
# max_sr_vol = vol_arr[sharpe_arr.argmax()]
#
# min_vol_ret = ret_arr[vol_arr.argmin()]
# min_vol_vol = vol_arr[vol_arr.argmin()]
#

# plt.figure(figsize=(12,8))
# plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='viridis')
# plt.colorbar(label='Sharpe Ratio')
# plt.xlabel('Volatility')
# plt.ylabel('Return')
# plt.scatter(max_sr_vol, max_sr_ret,c='red', s=50, marker="*")
# plt.scatter(min_vol_vol, min_vol_ret,c='blue', s=50, marker="D")
# plt.show()


from scipy import optimize

def get_ret_vol_sr(weights):
    weights = np.array(weights)
    ret = np.sum(log_ret.mean() * weights) * 252
    vol = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov()*252, weights)))
    sr = ret/vol
    return np.array([ret, vol, sr])

def neg_sharpe(weights):

    return get_ret_vol_sr(weights)[2] * -1

def check_sum(weights):
    #return 0 if sum of the weights is 1
    return np.sum(weights)-1

def minimize_volatility(weights):
    return get_ret_vol_sr(weights)[1]


cons = ({'type':'eq', 'fun': check_sum})
bounds = tuple((0, 1) for _ in range(len(tickers))) # Weights must be between 0 and 1
init_guess = [1/len(tickers) for _ in range(len(tickers))]

opt_results = optimize.minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
print(opt_results)
print(opt_results['fun'])


returns = np.linspace(0, 0.3, 200) # Returns between 0 and 30%
# returns = np.linspace(ret_arr.min(), ret_arr.max(), 200)
vols = []
weights = []

for r in returns:
    cons = ({'type':'eq', 'fun': check_sum}, # Weights sum to 0
            {'type':'eq', 'fun': lambda w: get_ret_vol_sr(w)[0] - r}) # We only want vol at specific return values, the eq must be 0 so by subtracting r and ensuring it is 0 we know we are optimizing for that specific return

    opt_results = optimize.minimize(minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
    vols.append(opt_results['fun'])
    weights.append(opt_results['x'])


returns = np.array(returns)
vols = np.array(vols)
weights = np.array(weights)
sharpes = returns/vols

max_sr_ret = returns[sharpes.argmax()]
max_sr_vol = vols[sharpes.argmax()]
max_sr_weights = weights[sharpes.argmax()]

min_vol_ret = returns[vols.argmin()]
min_vol_vol = vols[vols.argmin()]
min_vol_weights = weights[vols.argmin()]

print("Max Sharpe:", {k:v for k, v in zip(tickers, max_sr_weights.round(3))}, "\nMin Vol:", {k:v for k, v in zip(tickers, min_vol_weights.round(3))})

plt.figure(figsize=(12,8))
plt.title("Efficient Frontier")
plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='viridis')
plt.colorbar(label='Sharpe Ratio')
plt.xlabel('Volatility')
plt.ylabel('Return')
plt.plot(vols,returns, 'r--', linewidth=3)
plt.scatter(max_sr_vol, max_sr_ret, c='black', s=50, marker="*")
plt.scatter(min_vol_vol, min_vol_ret,c='black', s=50, marker="D")

graph_name = "_".join(tickers)
plt.savefig(f'ef_graphs/{graph_name}.png')
plt.show()
