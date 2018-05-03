import glob
import importlib
import inspect
import json
import logging
import os
import pandas as pd
import re
import rlog
import sys

import omega_ui.configuration as oc
import omega_ui.tearsheet as ots

users_file = 'users.json'
log_dir = os.path.join(oc.cfg['logging']['root'], 'app')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


# Backtest class
btm = importlib.import_module(oc.cfg['default']['backtest'])
backtest = btm.FuturesBacktest()


class LogFileCreator:
    def __init__(self):
        files = glob.glob(os.path.join(log_dir, 'backtest*.txt'))
        if len(files) > 0:
            last = max(files, key=os.path.getctime)
            nb = re.findall(r'\d+', last)
            self.counter = int(nb[0]) + 1
        else:
            # If no files, start at 1
            self.counter = 1

    def next_file_name(self):
        self.counter += 1
        return log_dir + '/backtest{:03d}-logs.txt'.format(self.counter)

    @staticmethod
    def werkzeug_log_file_name():
        return log_dir+'/access.log'


def test_list(module_name):
    try:
        result = []
        importlib.import_module(module_name)
        for name, obj in inspect.getmembers(sys.modules[module_name]):
            if inspect.isclass(obj):
                result.append(name)
        return result
    except:
        return []


def create_ts(uid, module_name, strategy_name, symbols, cash):
    result = []
    logger = logging.getLogger()
    lfc = LogFileCreator()
    fh = logging.FileHandler(lfc.next_file_name())
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    fh.setLevel(logging.NOTSET)
    logger.addHandler(fh)
    rh = rlog.RedisHandler(channel='l' + uid)
    logger.addHandler(rh)
    logger.log(logging.DEBUG, 'start')
    try:
        # Get strategy
        module = importlib.import_module(module_name)
        importlib.reload(module)  # Always reload module in case some changes have been made to the strategies
        strategy = getattr(module, strategy_name)
        # Backtest
        params = backtest.get_parameters(symbols)  # Params need to be extracted from the UI
        returns, transactions, pnl = backtest.run(symbols, cash, strategy, **params)
        transactions.reset_index(inplace=True)
        result = json.dumps({
            'returns': returns.to_json(),
            'transactions': transactions.to_json(),
            'title': '{}: {:,.2f}'.format(symbols, pnl)
        })
        logger.log(logging.DEBUG, 'done')
    except Exception as e:
        logger.log(logging.ERROR, str(e))
    logger.removeHandler(fh)
    logger.removeHandler(rh)
    return result


def extract_figure(json_ts, w, h):
    try:
        ts = json.loads(json_ts)
        df_r = pd.read_json(ts['returns'], typ='series').rename('return')
        fig = ots.create_figure(df_r, ts['title'])
        fig['layout'].update(autosize=True, width=w, height=h)

        return fig
    except:
        return []


def extract_statistic(json_ts):
    try:
        ts = json.loads(json_ts)
        df_r = pd.read_json(ts['returns'], typ='series').rename('return')
        df_t = pd.read_json(ts['transactions'])
        return ots.create_statistic(df_r, df_t)
    except:
        return dict(
            Curve={
                'Total Return': 0,
                'CAGR': 0,
                'Sharpe Ratio': 0,
                'Annual Volatility': 0,
                'SQN': 0,
                'R-Squared': 0,
                'Max Daily Drawdown': 0,
                'Max Drawdown Duration': 0,
                'Trades Per Year': 0
            },
            Trade={
                'Trade Winning %': 0,
                'Average Trade': 0,
                'Average Win': 0,
                'Average Loss':0,
                'Best Trade': 0,
                'Worst Trade': 0,
                'Worst Trade Date': 0,
                'Avg Days in Trade': 0,
                'Trades': 0
            },
            Time={
                'Winning Months %': '',
                'Average Winning Month %': 0,
                'Average Losing Month %': 0,
                'Best Month %': 0,
                'Worst Month %': 0,
                'Winning Years %': 0,
                'Best Year %': 0,
                'Worst Year %': 0
            })


def get_users_list():
    with open(users_file) as data_file:
        data = json.load(data_file)
        return data


def add_user(username, password):
    users = get_users_list()
    users[username] = password
    with open(users_file, 'w') as outfile:
        json.dump(users, outfile, indent=2)


def get_users():
    result = []
    users = get_users_list()
    for key in users:
        result.append([key, users[key]])
    return result
