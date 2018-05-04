# Omega UI

Backtesting Front End for backtrader (see: https://www.backtrader.com/). Built with Plotly/Dash.

**Important:** Before using, please make sure to update the file **omega-ui.config** at the root of the omega_ui folder.
This file contains configuration parameters that are used throughout the application. A Redis instance must be
running (this is used to display logs) and the package folder needs to be in PythonPath.

What needs to be updated:
* Default/Backtest: This is the module implementing the Backtest class.
* Default/Redis: IP address of the Redis datastore.
* Logging/Root: Path to where logs will be stored.
* Backtest/Cash: Default cash value.


1. Installation:
From pypi: pip install omega_ui


2. Usage:
  * Before the UI can be used, the Backtest class needs to be implemented. This is done by inheriting the class Backtest
from omega_ui.backtest and implementing its methods:
    * get_symbols: Symbols that will be displayed on the UI and on which we can run a backtest.
    * get_parameters: Default parameters for a given strategy.
    * run: Run a backtest. Please note that this needs to return 3 items: returns, transactions and pnl.

  * Before running the UI, the following command has to be running: 'python socket_logged.py flask run'. This is the
  server for the logs.