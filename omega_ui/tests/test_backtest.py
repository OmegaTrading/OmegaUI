import logging
import os
import pandas as pd

import backtrader as bt

import omega_ui.backtest as ob


class TestStrategy(bt.Strategy):
    """Test Strategy to check data is loaded correctly"""
    params = (('param1', 10), ('param2', 20))

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.date = self.datas[0].datetime.date
        self.dataclose = self.datas[0].close
        self.order = None  # To keep track of pending orders
        self.log(logging.INFO, 'Strategy Initialized!')
        self.log(logging.INFO, 'Param1: {} - Param2: {}'.format(self.p.param1, self.p.param1))

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
        return ['AAPL', 'MSFT']

    def get_parameters(self, strategy, symbols):
        return {'param1': 10, 'param2': 20}

    def run(self, symbols, cash, strategy, **params):
        path_dir = os.path.dirname(os.path.realpath(__file__))
        # Setup Cerebro
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(cash)
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
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
        strat = results[0]
        pyfoliozer = strat.analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
        return returns, transactions, pnl


