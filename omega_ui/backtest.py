import backtrader as bt


class Backtest(object):
    """Backtest class - Inherit and implement this class to run a backtest."""
    def __init__(self):
        pass

    def get_symbols(self):
        """Get a list of symbols to run a backtest on

        :return: list - List of symbols for the backtest
        """
        pass

    def get_parameters(self, strategy, symbols):
        """Get parameters for the backtest

        :param strategy: object - Strategy to run the backtest on
        :param symbols: list - List of symbols
        :return: dict - Parameters dictionary to be displayed in the UI
        """
        pass

    def run(self, symbols, cash, strategy, **params):
        """Run a backtest

        :param symbols: list - List of symbols
        :param cash: float - Starting cash value
        :param strategy: object - Strategy to run the backtest on
        :param params: dict - Parameters dictionary to be displayed in the UI
        :return: float/results - Returns 2 items: PnL and Results from a cerebro backtest
        """
        pass

    @staticmethod
    def setup_cerebro(cash):
        """Setup a Cerebro instance with a starting cash value and all the necessary analyzers.

        :param cash: float - Starting cash value
        :return: object - Cerebro
        """
        # Setup Cerebro
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(cash)
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        return cerebro
