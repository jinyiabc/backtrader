import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.strategies as btstrats

data = btfeeds.WindCSVData(
    dataname='./datas/000504.SZ.CSV',
    datetime=2,
    time=-1,  # position of time
    open=3,  # position of open
    high=4,
    low=5,
    close=6,
    volume=7,
    openinterest=-1,  # -1 for not present
    timeframe=bt.TimeFrame.Days)


cerebro = bt.Cerebro()

cerebro.adddata(data)  # a 'name' parameter can be passed for plotting purposes

# strategy
cerebro.addstrategy(btstrats.MA_CrossOver)

cerebro.run(preload=False)

cerebro.plot()