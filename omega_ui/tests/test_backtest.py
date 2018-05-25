import logging
import os
import pandas as pd

import backtrader as bt

import omega_ui.backtest as ob


class StatsTest(bt.Strategy):
    """
    Test Strategy to check some statistics

    This strategy should be used with TestData.csv

    TestData.csv will rise from 1 dollar to 101 dollars over 20 bars then fall
    from 101 to 1 over the next 20 bars. (40 bar round trip). The pattern will
    repeat in a loop until the end of the data set.

    The first two bars close/open at 1 dollar to ease testing with market orders
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.date = self.datas[0].datetime.date
        self.dataclose = self.datas[0].close
        self.buy_bars = [1, 21, 41, 61]
        self.close_bars = [20, 40, 60, 80]
        self.sell_bars = []
        self.log(logging.INFO, 'Strategy Initialized!')

    def next(self):
        bar = len(self.data)
        if bar in self.buy_bars:
            print('Buying On Bar {} Price = {}'.format(bar, self.dataclose[0]))
            self.buy(stake=1)
            self.log(logging.INFO, 'Buy @ {}'.format(self.dataclose[0]))
        elif bar in self.close_bars:
            print('Closing On Bar {} Price = {}'.format(bar, self.dataclose[0]))
            self.close(stake=1)
            self.log(logging.INFO, 'Exit @ {}'.format(self.dataclose[0]))
        else:
            pass

    def log(self, level, message):
        self.logger.log(level, '{} - {}'.format(self.date(0), message))


class TestStrategy(bt.Strategy):
    """Test Strategy to check data is loaded correctly"""
    params = (('param1', 10), ('param2', 20))

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.date = self.datas[0].datetime.date
        self.dataclose = self.datas[0].close
        self.order = None  # To keep track of pending orders
        self.log(logging.INFO, 'Strategy Initialized!')
        self.log(logging.INFO, 'Param1: {} - Param2: {}'.format(self.p.param1, self.p.param2))

    def log(self, level, message):
        self.logger.log(level, '{} - {}'.format(self.date(0), message))

    def next(self):
        if self.order:
            return
        # Debugging
        self.log(logging.DEBUG, 'Close price: {}'.format(self.dataclose[0]))

        # Current close less than previous close
        if self.dataclose[0] < self.dataclose[-1]:
            # Previous close less than the previous close
            if self.dataclose[-1] < self.dataclose[-2]:
                self.log(logging.INFO, 'Buy @ {}'.format(self.dataclose[0]))
                self.order_target_percent(target=0.25)
        # Current close greater than previous close
        if self.dataclose[0] > self.dataclose[-1]:
            # Previous close greater than the previous close
            if self.dataclose[-1] > self.dataclose[-2]:
                self.log(logging.INFO, 'Sell @ {}'.format(self.dataclose[0]))
                self.order_target_percent(target=-0.25)


class ExampleBacktest(ob.Backtest):
    def get_symbols(self):
        return ['AAPL', 'MSFT', 'TestData']

    def get_parameters(self, strategy, symbols):
        return {'param1': 10, 'param2': 20}

    def run(self, symbols, cash, strategy, **params):
        path_dir = os.path.dirname(os.path.realpath(__file__))
        # Setup Cerebro
        cerebro = ob.Backtest.setup_cerebro(cash)
        # Add Data
        for s in symbols:
            df = pd.read_csv(os.path.join(path_dir, '{}.csv'.format(s)), parse_dates=True, index_col=0)
            data = bt.feeds.PandasData(dataname=df)
            cerebro.adddata(data)
        # Strategy
        cerebro.addstrategy(strategy, **params)
        # Backtest
        results = cerebro.run()
        pnl = cerebro.broker.getvalue() - cash

        return pnl, results[0]
