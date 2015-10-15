from matplotlib import pylab
import numpy as np
import pandas as pd
import DataAPI
import seaborn as sns
sns.set_style('white')

start = datetime(2015, 4, 1)
end = datetime(2015, 8, 31)
benchmark = 'HS300'
universe = set_universe('SH50')
capital_base = 1000000
refresh_rate = 1
window = 1

initMACD = -10000.0
histMACD = pd.DataFrame(initMACD, index = universe, columns = ['preShortEMA', 'preLongEMA', 'preDIF', 'preDEA'])
shortWin = 26    # 短期EMA平滑天数
longWin  = 52    # 长期EMA平滑天数
macdWin  = 15    # DEA线平滑天数

longest_history = window

def initialize(account):
    #account.amount = 10000
    account.universe = universe
    account.days = 0
    
def handle_data(account):
    account.days = account.days+1
    sell_list = []
    buy_list = []
    for stk in account.universe:
        all_close_prices = account.get_attribute_history('closePrice', 1)
        prices = all_close_prices[stk]
        if prices is None:
            continue
        
        preShortEMA = histMACD.at[stk, 'preShortEMA']
        preLongEMA = histMACD.at[stk, 'preLongEMA']
        preDIF = histMACD.at[stk, 'preDIF']
        preDEA = histMACD.at[stk, 'preDEA']
        if preShortEMA == initMACD or preLongEMA == initMACD:
            histMACD.at[stk, 'preShortEMA'] = prices[-1]
            histMACD.at[stk, 'preLongEMA'] = prices[-1]
            histMACD.at[stk, 'preDIF'] = 0
            histMACD.at[stk, 'preDEA'] = 0
            return
            
        shortEMA = preShortEMA*1.0*(shortWin-1)/(shortWin+1) + prices[-1]*2.0/(shortWin+1)
        longEMA = preLongEMA*1.0*(longWin-1)/(longWin+1) + prices[-1]*2.0/(longWin+1)
        DIF = shortEMA - longEMA
        DEA = preDEA*1.0*(macdWin-1)/(macdWin+1) + DIF*2.0/(macdWin+1)
        
        histMACD.at[stk, 'preShortEMA'] = shortEMA
        histMACD.at[stk, 'preLongEMA'] = longEMA
        histMACD.at[stk, 'preDIF'] = DIF
        histMACD.at[stk, 'preDEA'] = DEA
        
        if account.days > longWin and account.days%1 == 0:
            #if DIF > 0 and DEA > 0 and preDIF > preDEA and DIF < DEA:
            if preDIF > preDEA and DIF < DEA:     
                sell_list.append(stk)
            #if DIF < 0 and DEA < 0 and preDIF < preDEA and DIF > DEA:
            if preDIF < preDEA and DIF > DEA:
                buy_list.append(stk)
    

	
    for stock in sell_list:
        order_to(stock, 0)
        
    for stock in buy_list:
        amount = int((account.cash/len(buy_list))/prices[-1]/100)*100
        order(stock, amount)    
    
    #print('buylist',buylist)
    #print(change)
    #print(account.position)
