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
        :return: pandas/pandas/float - Returns 3 items: Returns, Transactions and PnL
        """
        pass
