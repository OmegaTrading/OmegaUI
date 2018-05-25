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
log_dir = oc.cfg['logging']['root']
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


# Backtest class
btm = importlib.import_module(oc.cfg['default']['module'])
backtest = getattr(btm, oc.cfg['default']['class'])()


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
        return os.path.join(log_dir, 'backtest{:03d}-logs.txt'.format(self.counter))

    @staticmethod
    def werkzeug_log_file_name():
        return os.path.join(log_dir, 'access.log')


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


def cash_param():
    return [{'Parameter': 'Cash', 'Value': oc.cfg['backtest']['cash']}]


def params_list(module_name, strategy_name, symbol):
    logger = logging.getLogger(__name__)

    params = cash_param()
    try:
        # Get strategy
        module = importlib.import_module(module_name)
        importlib.reload(module)  # Always reload module in case some changes have been made to the strategies
        strategy = getattr(module, strategy_name)
        for key, value in backtest.get_parameters(strategy, symbol).items():
            if isinstance(value, dict):
                value = json.dumps(value)
            params.append({'Parameter': key, 'Value': value})
    except Exception as e:
        logger.log(logging.ERROR, 'Error in loading params: {}!'.format(str(e)))
    return params


def create_ts(uid, module_name, strategy_name, symbols, params):
    result = []
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
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
        cash = float(params.pop('Cash', 1))
        for k, v in params.items():
            params[k] = json.loads(v)
        pnl, strat = backtest.run(symbols, cash, strategy, **params)
        pyfoliozer = strat.analyzers.getbyname('pyfolio')
        returns, _, _, _ = pyfoliozer.get_pf_items()
        result = json.dumps({
            'returns': returns.to_json(),
            'statistic': ots.create_statistic(returns,strat),
            'title': '{}: {:,.2f}'.format(symbols, pnl)
        })
        logger.log(logging.DEBUG, 'done')
    except Exception as e:
        logger.log(logging.ERROR, 'Error in starting a backtest: {}'.format(str(e)))
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
        return ts['statistic']
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
                'Average Loss': 0,
                'Best Trade': 0,
                'Worst Trade': 0,
                'Worst Trade Date': 0,
                'Avg Days in Trade': 0,
                'Trades': 0
            },
            Time={
                'Winning Months %': 0,
                'Average Winning Month %': 0,
                'Average Losing Month %': 0,
                'Best Month %': 0,
                'Worst Month %': 0,
                'Winning Years %': 0,
                'Best Year %': 0,
                'Worst Year %': 0
            })


def get_users_list():
    try:
        with open(users_file) as data_file:
            data = json.load(data_file)
            return data
    except:
        return {}


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
