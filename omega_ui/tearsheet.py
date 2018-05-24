import plotly.graph_objs as go
import plotly.tools as pto
import numpy as np
import empyrical as ep
import pandas as pd


def create_figure(returns, title):
    """
        Creates figure with graphics: drawdown, underwater, heat map with month returns and revenue by year.
        :param returns: pd.Series or np.ndarray
            Daily returns of the strategy, noncumulative.
        :param title: string
            Header of tearsheet
        :return: Figure
             Plotly figure that could be displayed using plot or iplot
    """
    df = returns.to_frame()
    df['year'] = df.index.year
    df['month'] = df.index.month

    # plot drawdown
    df_cum_rets = ep.cum_returns(returns, starting_value=1.0)
    drawdown = go.Scatter(
        x=df_cum_rets.index,
        y=df_cum_rets,
        line=dict(
            color='#66B266',
            width=2),
        name=''
    )

    # plot underwater
    running_max = np.maximum.accumulate(df_cum_rets)
    underwater = -100 * ((running_max - df_cum_rets) / running_max)
    uw = go.Scatter(
        x=underwater.index,
        y=underwater,
        fill='tonexty',
        line=dict(
            color='#FF6A6A',
            width=2),
        name=''
    )

    pivot_for_hm = pd.pivot_table(
        df,
        index='year',
        columns='month',
        values='return',
        aggfunc=np.sum
    ).fillna(0).apply(lambda x: x * 100)

    custom_color_scale = [
        [0.0, '#C41E27'],
        [0.1111111111111111, '#EA5739'],
        [0.2222222222222222, '#FA9B58'],
        [0.3333333333333333, '#FCAA5F'],
        [0.4444444444444444, '#FEE28F'],
        [0.5555555555555556, '#FEFFBE'],
        [0.6666666666666666, '#C3E67D'],
        [0.7777777777777778, '#73C264'],
        [0.8888888888888888, '#0E8245'],
        [1.0, '#006837']
    ]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    hover = pivot_for_hm.values.astype(str)
    for x in range(len(pivot_for_hm.index)):
        for y in range(len(months)):
            hover[x][y] = '{} {}: {:,.2f}'.format(pivot_for_hm.index[x], months[y], pivot_for_hm.values[x][y])

    heat_map = go.Heatmap(
        z=pivot_for_hm.values.tolist(),
        colorscale=custom_color_scale,
        showscale=False,
        x=months,
        y=pivot_for_hm.index,
        text=hover,
        hoverinfo='text',
        name=''
    )

    annotations = []
    for n, row in enumerate(pivot_for_hm.values.tolist()):
        for m, val in enumerate(row):
            annotations.append(
                go.Annotation(
                    text='%0.1f' % pivot_for_hm.values.tolist()[n][m],
                    x=pivot_for_hm.columns[m] - 1,
                    y=pivot_for_hm.index[n],
                    xref='x3',
                    yref='y3',
                    font=dict(color='#000'),
                    showarrow=False)
            )

    # plot revenue by year
    df_rby = df.groupby(['year'])[['return']].sum().apply(lambda x: x * 100)
    revenue_by_year = go.Bar(
        x=df_rby.index,
        y=df_rby['return'],
        marker=dict(color='#44F'),
        name=''
    )

    # draw all plots on the same figure
    fig = pto.make_subplots(
        rows=3,
        cols=4,
        specs=[
            [{'colspan': 4}, None, None, None],
            [{'colspan': 4}, None, None, None],
            [{'colspan': 3}, None, None, {}]
        ],
        subplot_titles=('', 'Drawdown (%)', 'Monthly Returns (%)', 'Yearly Returns (%)'),
        horizontal_spacing=0.05,
        vertical_spacing=0.05,
        print_grid=False,
    )

    # place graphs
    fig.append_trace(drawdown, 1, 1)
    fig.append_trace(uw, 2, 1)
    fig.append_trace(heat_map, 3, 1)
    fig.append_trace(revenue_by_year, 3, 4)

    fig['layout'].update(
        autosize=False,
        width=1000,
        height=1200
    )

    fig['layout'].update(showlegend=False, title=title)
    fig['layout']['yaxis1']['tickformat'] = '.2f'
    fig['layout']['xaxis1']['tickformat'] = '%Y-%m-%d'
    fig['layout']['yaxis2']['tickformat'] = '.2f'
    fig['layout']['xaxis2']['tickformat'] = '%Y-%m-%d'
    fig['layout']['yaxis4']['tickformat'] = '.2f'
    fig['layout']['yaxis3']['autorange'] = 'reversed'  # direction of years on the heat map
    fig['layout']['yaxis3']['dtick'] = 1  # show all ticks
    fig['layout']['xaxis4']['dtick'] = 1  # show all ticks
    fig['layout']['xaxis4']['tickangle'] = -45  # rotate ticks
    fig['layout']['annotations'].extend(annotations)
    fig['layout']['margin']['l'] = 40
    fig['layout']['margin']['r'] = 20
    fig['layout']['margin']['t'] = 40
    fig['layout']['margin']['b'] = 40

    return fig


def create_statistic(returns, results):
    """
        Calculates different metrics for strategy
        :param returns: pd.Series or np.ndarray
            Daily returns of the strategy, noncumulative.
        :param results: object
            Results from a backtrader backtest
        :return: metrics based on returns and trades
    """
    df = returns.to_frame()
    df['year'] = df.index.year
    df['month'] = df.index.month
    # Analysis
    sqn_analysis = results.analyzers.SQN.get_analysis()
    dd_analysis = results.analyzers.drawdown.get_analysis()
    trades = results.analyzers.trades.get_analysis()
    df_cum_rets = ep.cum_returns(returns, starting_value=1.0)
    returns_by_month = df.groupby(['year', 'month'])['return'].sum()
    df_rby = df.groupby(['year'])[['return']].sum().apply(lambda x: x * 100)
    return dict(
        Curve={
            'Total Return': round((df_cum_rets.iloc[-1] - 1) * 100, 2),
            'CAGR': round(ep.cagr(returns) * 100, 2),
            'Sharpe Ratio': round(ep.sharpe_ratio(returns), 2),
            'Annual Volatility': round(ep.annual_volatility(returns) * 100, 2),
            'SQN': round(sqn_analysis['sqn'], 2),
            'R-Squared': round(ep.stability_of_timeseries(returns), 2),
            'Max Daily Drawdown': round(dd_analysis['max']['drawdown'], 2),
            'Max Drawdown Duration': dd_analysis['max']['len'],
            'Trades Per Year': 0  # TODO
        },
        Trade={
            'Trade Winning %': round(trades['won']['total'] / trades['total']['total'] * 100, 2),
            'Average Trade': round(trades['pnl']['net']['average'], 2),
            'Average Win': round(trades['won']['pnl']['average'], 2),
            'Average Loss': round(trades['lost']['pnl']['average'], 2),
            'Best Trade': round(trades['won']['pnl']['max'], 2),
            'Worst Trade': round(trades['lost']['pnl']['max'], 2),
            'Worst Trade Date': 0,  # TODO
            'Avg Days in Trade': round(trades['len']['average'], 2),
            'Trades': trades['total']['total']
        },
        Time={
            'Winning Months %': round(len(returns_by_month.loc[lambda x: x > 0]) / len(returns_by_month.index) * 100, 2),
            'Average Winning Month %': round(returns_by_month.loc[lambda x: x > 0].mean() * 100, 2),
            'Average Losing Month %': round(returns_by_month.loc[lambda x: x < 0].mean() * 100, 2),
            'Best Month %': round(returns_by_month.max() * 100, 2),
            'Worst Month %': round(returns_by_month.min() * 100, 2),
            'Winning Years %': round(len(df_rby[df_rby['return'] > 0].index) / len(df_rby.index) * 100, 2),
            'Best Year %': round(df_rby.max()['return'], 2),
            'Worst Year %': round(df_rby.min()['return'], 2),
        }
    )


def create_tearsheet(results, title):
    """
        Creates tearsheet with graphics: drawdown, underwater, heat map with month returns, revenue by year and also,
        calculates different metrics for strategy
        :param results: object
            Results from a backtrader backtest
        :param title: string
            Header of tearsheet
        :return: Dictionary
            Dictionary with two records
             fig: plotly figure that could be displayed using plot or iplot
             statistics: metrics based on returns and trades
    """
    pyfoliozer = results.analyzers.getbyname('pyfolio')
    returns, _, _, _ = pyfoliozer.get_pf_items()

    return {'fig': create_figure(returns, title), 'statistics': create_statistic(returns, results)}
