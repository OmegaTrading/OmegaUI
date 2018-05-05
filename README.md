# Omega UI

Backtesting Front End for backtrader (see: https://www.backtrader.com/). Built with Plotly/Dash.

**Important:**
* Before using, please make sure to update the file **omega-ui.config** at the root of the omega_ui folder.
This file contains configuration parameters that are used throughout the application.
* A Redis instance must be running (this is used to display logs) and the package folder needs to be in PythonPath.

**What needs to be updated:**
* Default/Module: This is the module where the class implementing the Backtest class is (make sure that the module is in
PythonPath).
* Default/Class: Name of the class implementing the Backtest class.
* Default/Redis: IP address of the Redis datastore (Default port: 6379).
* Logging/Root: Path to where logs will be stored.
* Backtest/Cash: Default cash value.
* Backtest/Modules: Modules where the strategies are located (several modules can be implemented using commas as
a delimiter).


## 1. Installation:
From pypi: pip install omega_ui

From source: Place the omega_ui directory found in the sources inside your project

## 2. Usage:
  * Before the UI can be used, the Backtest class needs to be implemented. This is done by inheriting the class Backtest
from omega_ui.backtest and implementing the following methods:
    * get_symbols: Symbols that will be displayed on the UI and on which we can run a backtest.
    * get_parameters: Default parameters for a given strategy.
    * run: Run a backtest. Please note that this needs to return 3 items: returns, transactions and pnl.

  * Before running the UI, the following command has to be running: 'python socket_logged.py flask run'. This is the
  server which redirects the logs to the UI.


## 3. Example:
An example has been included in the tests folder to give an idea on how to use the UI (see test_backtest.py). When
using it, please make sure to select the strategy "TestStrategy" in the Strategy dropwdown as selecting ExampleBacktest
would not work.