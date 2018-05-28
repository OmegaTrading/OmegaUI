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
From source: Place the omega_ui directory found in the sources inside your project

## 2. Usage:
  * Before the UI can be used, the Backtest class needs to be implemented. This is done by inheriting the class Backtest
from omega_ui.backtest and implementing the following methods:
  * get_symbols: Symbols that will be displayed on the UI and on which we can run a backtest.
  * get_parameters: Default parameters for a given strategy.
  * run: Run a backtest. Please note that this needs to return 2 items: returns and results from backtrader.

  * Before running the UI, the following command has to be running: 'python socket_logging.py flask run'. This is the
server which redirects the logs to the UI.

  * To run the UI, run the following command: 'python app.py' and in your browser (tested only on Chrome), navigate to
the specified address (should be http://127.0.0.1:8050/).

## 3. Example:
An example has been included in the tests folder to give an idea on how to use the UI (see test_backtest.py). When
using it, please make sure to select the strategy "TestStrategy" in the Strategy dropwdown as selecting ExampleBacktest
would not work.

## Note:
This project is designed for people already comfortable using and writing python code. I do not have time to provide
support but am happy to help if you get in touch regarding the following topics:
  * Error messages
  * Documentation
  * Suggestions for extra features
  * Bugs
I will try to reply to messages but can't guarantee it (as long as the message is properly formatted). This is a work
in progress and also a project which I use for my research. Offers to contribute will be accepted.

Also, if nothing happens while trying to run a backtest, this might be due to a problem with the Dash React part.
I had an issue where I had to roll back Dash to a specific version and haven't tried to use the latest version again.
To find out if there's a problem with React, right-click in Chrome and select Inspect, then navigate to the Console
tab and look for errors. See below to know which dash packages work with this application:
* dash==0.21.0
* dash-auth==0.1.0
* dash-core-components==0.20.2
* dash-html-components==0.10.0
* dash-renderer==0.11.3
* dash-table-experiments==0.6.0
