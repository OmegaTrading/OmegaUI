import setuptools as st

st.setup(
    name='omega_ui',
    version='0.0.8',
    packages=['omega_ui'],
    url='https://github.com/OmegaTrading/OmegaUI',
    license='GPL-3.0',
    author='OmegaUI',
    author_email='omegaui.trading@gmail.com',
    description='Front End for backtrader. Built with Plotly/Dash.',
    requires=[
        'backtrader', 'dash', 'dash_auth', 'dash_core_components', 'dash_html_components', 'dash_table_experiments',
        'eventlet', 'empyrical', 'flask', 'flask_socketio', 'numpy', 'pandas', 'plotly', 'redis', 'rlog', 'yaml'
    ]
)
