class Backtest(object):
    """Backtest class - Inherit and implement this class to run a backtest."""
    def __init__(self):
        pass

    def get_symbols(self):
        pass

    def get_parameters(self, symbols):
        pass

    def run(self, symbols, cash, strategy, **params):
        pass

