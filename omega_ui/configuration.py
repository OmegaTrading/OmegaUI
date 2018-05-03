import os
import sys
import yaml


"""Configuration module

This module is used to load the configuration as defined in the config file.
"""
cfg = []


def initialization():
    """Read and return configuration file."""
    global cfg

    # Configuration
    root = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(root, 'omega_ui.config'), 'r') as y_cfg:
            cfg = yaml.load(y_cfg)
    except FileNotFoundError:
        print('Configuration file not found!')
        sys.exit(1)


# Read configuration
initialization()
