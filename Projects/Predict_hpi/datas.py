########################################################################

import pandas as pd
import numpy as np
import time
import os
import requests
from data_keys import *

########################################################################

# Data-directory. Set this before calling any of the load-functions.
data_dir = 'data/'

# Data-directory for intraday share-prices.
data_dir_intraday = os.path.join(data_dir, 'intraday/')

########################################################################


def _resample_daily(data):
    return data.resample('D').interpolate(method='linear')


def _load_data(path):

    data = pd.read_csv(path,
                       sep="\t",
                       index_col=0,
                       parse_dates=True,
                       dayfirst=False)

    return data


########################################################################
# Public functions.


def load_usa_cpi():

    # Path for the data-file to load.
    path = os.path.join(data_dir, "USA CPI.csv")

    # Load the data.
    data = pd.read_csv(path, sep=",", parse_dates=[3], index_col=3)

    # Rename the index- and data-columns.
    data.index.name = "Date"
    data.rename(columns={"Value": CPI}, inplace=True)

    # Resample by linear interpolation to get daily values.
    data_daily = _resample_daily(data[CPI])

    return data_daily

########################################################################
