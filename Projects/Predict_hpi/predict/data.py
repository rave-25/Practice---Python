########################################################################
#
# Functions for loading financial data.
#
# Data from several different files are combined into a single
# Pandas DataFrame for each stock or stock-index.
#
# The price-data is read from CSV-files from Yahoo Finance.
# Other financial data (Sales Per Share, Book-Value Per Share, etc.)
# is read from tab-separated text-files with date-format MM/DD/YYYY.
#
########################################################################
#
# This file is part of FinanceOps:
#
# https://github.com/Hvass-Labs/FinanceOps
#
# Published under the MIT License. See the file LICENSE for details.
#
# Copyright 2018 by Magnus Erik Hvass Pedersen
#
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
# Private helper-functions.


def _resample_daily(data):
    """
    Resample data using linear interpolation.

    :param data: Pandas DataFrame or Series.
    :return: Resampled daily data.
    """
    return data.resample('D').interpolate(method='linear')


def _load_data(path):
    """
    Load a CSV-file with tab-separation, date-index is in first column
    and uses the MM/DD/YYYY.

    This is a simple wrapper for Pandas.read_csv().

    :param path: Path for the data-file.
    :return: Pandas DataFrame.
    """
    data = pd.read_csv(path,
                       sep="\t",
                       index_col=0,
                       parse_dates=True,
                       dayfirst=False)

    return data


def _load_price_yahoo(ticker):
    """
    Load share-price data from a Yahoo CSV-file.

    Only retrieve the 'Close' and 'Adj Close' prices
    which are interpolated to daily values.

    The 'Close' price-data is adjusted for stock-splits.

    The 'Adj Close' price-data is adjusted for both
    stock-splits and dividends, so it corresponds to
    the Total Return.

    https://help.yahoo.com/kb/SLN2311.html

    :param ticker: Ticker-name for the data to load.
    :return: Pandas DataFrame with SHARE_PRICE and TOTAL_RETURN
    """

    # Path for the data-file to load.
    path = os.path.join(data_dir, ticker + " Share-Price (Yahoo).csv")

    # Read share-prices from file.
    price_raw = pd.read_csv(path,
                            index_col=0,
                            header=0,
                            sep=',',
                            parse_dates=[0],
                            dayfirst=False)

    # Rename columns.
    columns = \
        {
            'Adj Close': TOTAL_RETURN,
            'Close': SHARE_PRICE
        }
    price = price_raw.rename(columns=columns)

    # Select the columns we need.
    price = price[[TOTAL_RETURN, SHARE_PRICE]]

    # Interpolate to get prices for all days.
    price_daily = _resample_daily(price)

    return price_daily


def _load_earnings_per_share(ticker, df, profit_margin=True):
    """
    Load the Earnings Per Share from a data-file and add it to the DataFrame.
    Also calculate the P/E ratio and profit margin.

    :param ticker:
        Name of the stock used in the filenames e.g. "WMT"

    :param df:
        Pandas DataFrame with SHARE_PRICE.

    :param profit_margin:
        Boolean whether to add the profit margin to the DataFrame.
        Requires that df already contains SALES_PER_SHARE.

    :return:
        None. Data is added to the `df` DataFrame.
    """

    # Load data.
    path = os.path.join(data_dir, ticker + " Earnings Per Share.txt")
    earnings_per_share = _load_data(path=path)

    # Add to the DataFrame (interpolated daily).
    df[EARNINGS_PER_SHARE] = _resample_daily(earnings_per_share)

    # Add valuation ratio to the DataFrame (daily).
    df[PE] = df[SHARE_PRICE] / df[EARNINGS_PER_SHARE]

    # Add profit margin to the DataFrame (daily).
    if profit_margin:
        df[PROFIT_MARGIN] = df[EARNINGS_PER_SHARE] / df[SALES_PER_SHARE]


def _load_sales_per_share(ticker, df):
    """
    Load the Sales Per Share from a data-file and add it to the DataFrame.
    Also calculate the P/Sales ratio and one-year growth in Sales Per Share.

    :param ticker:
        Name of the stock used in the filenames e.g. "WMT"

    :param df:
        Pandas DataFrame with SHARE_PRICE.

    :return:
        None. Data is added to the `df` DataFrame.
    """

    # Load data.
    path = os.path.join(data_dir, ticker + " Sales Per Share.txt")
    sales_per_share = _load_data(path=path)

    # Add to the DataFrame (interpolated daily).
    df[SALES_PER_SHARE] = _resample_daily(sales_per_share)

    # Add valuation ratio to the DataFrame (daily).
    df[PSALES] = df[SHARE_PRICE] / df[SALES_PER_SHARE]

    # Add growth to the DataFrame (daily).
    df[SALES_GROWTH] = df[SALES_PER_SHARE].pct_change(periods=365)


def _load_book_value_per_share(ticker, df):
    """
    Load the Book-Value Per Share from a data-file and add it to the DataFrame.
    Also calculate the P/Book ratio.

    :param ticker:
        Name of the stock used in the filenames e.g. "WMT"

    :param df:
        Pandas DataFrame with SHARE_PRICE.

    :return:
        None. Data is added to the `df` DataFrame.
    """

    # Load data.
    path = os.path.join(data_dir, ticker + " Book-Value Per Share.txt")
    book_value_per_share = _load_data(path=path)

    # Add to the DataFrame (interpolated daily).
    df[BOOK_VALUE_PER_SHARE] = _resample_daily(book_value_per_share)

    # Add valuation ratio to the DataFrame (daily).
    df[PBOOK] = df[SHARE_PRICE] / df[BOOK_VALUE_PER_SHARE]


def _load_dividend_TTM(ticker, df):
    """
    Load the Dividend Per Share TTM (Trailing Twelve Months) from a data-file and
    add it to the DataFrame. Also calculate some related valuation ratios.

    :param ticker:
        Name of the stock-index used in the filenames e.g. "S&P 500"

    :param df:
        Pandas DataFrame with SHARE_PRICE.

    :return:
        None. Data is added to the `df` DataFrame.
    """

    # Load data.
    path = os.path.join(data_dir, ticker + " Dividend Per Share TTM.txt")
    dividend_per_share_TTM = _load_data(path=path)

    # Add to the DataFrame (interpolated daily).
    df[DIVIDEND_TTM] = _resample_daily(dividend_per_share_TTM)

    # Add valuation ratios to the DataFrame (daily).
    df[PDIVIDEND] = df[SHARE_PRICE] / df[DIVIDEND_TTM]
    df[DIVIDEND_YIELD] = df[DIVIDEND_TTM] / df[SHARE_PRICE]


########################################################################
# Public functions.


def load_usa_cpi():
    """
    Load the U.S. Consumer Price Index (CPI) which measures inflation.
    The data is interpolated to get daily values.

    http://www.bls.gov/cpi/data.htm

    :return: Pandas DataFrame.
    """

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


def load_usa_gov_bond_1year():
    """
    Load the yields on U.S. Government Bonds with 1-year maturity.
    The data is interpolated to get daily values.

    :return: Pandas DataFrame.
    """

    # Path for the data-file to load.
    path = os.path.join(data_dir, "USA Gov Bond Yield 1-Year.txt")

    # Load the data.
    bond_yields = _load_data(path=path)

    # Remove rows with NA.
    bond_yields.dropna(inplace=True)

    # Scale the data so for example 0.035 in the data means 3.5%
    bond_yields /= 100

    # Resample by linear interpolation to get daily values.
    bond_yields_daily = _resample_daily(bond_yields)

    return bond_yields_daily


def load_index_data(ticker, sales=True, book_value=True, dividend_TTM=True):
    """
    Load data for a stock-index from several different files
    and combine them into a single Pandas DataFrame.

    - Price is loaded from a Yahoo-file.
    - Dividend, Sales Per Share, Book-Value Per Share, etc.
      are loaded from separate files.

    The Total Return is produced from the share-price and dividend.
    The P/Sales and P/Book ratios are calculated daily.

    Note that dividend-data is often given quarterly for stock
    indices, but the individual companies pay dividends at different
    days during the quarter. When calculating the Total Return we
    assume the dividend is paid out and reinvested quarterly.
    There is probably a small error from this. We could instead
    spread the quarterly dividend evenly over all the days in
    the quarter and reinvest these small portions daily. Perhaps
    this would create a smaller estimation error. It could be
    tested if this is really a problem or if the estimation error
    is already very small.

    :param ticker:
        Name of the stock-index used in the filenames e.g. "S&P 500"

    :param sales:
        Boolean whether to load data-file for Sales Per Share.

    :param book_value:
        Boolean whether to load data-file for Book-Value Per Share.

    :param dividend_TTM:
        Boolean whether to load data-file for Dividend Per Share TTM.

    :return:
        Pandas DataFrame with the data.
    """

    # Load price.
    price_daily = _load_price_yahoo(ticker=ticker)

    # Load dividend.
    path = os.path.join(data_dir, ticker + " Dividend Per Share.txt")
    dividend_per_share = _load_data(path=path)

    # Merge price and dividend into a single DataFrame.
    df = pd.concat([price_daily, dividend_per_share], axis=1)

    # Only keep the rows where the share-price is defined.
    df.dropna(subset=[SHARE_PRICE], inplace=True)

    # Calculate the Total Return.
    # The price-data from Yahoo does not contain the Total Return
    # for stock indices because it does not reinvest dividends.
    df[TOTAL_RETURN] = returns.total_return(df=df)

    # Load Sales Per Share data.
    if sales:
        _load_sales_per_share(ticker=ticker, df=df)

    # Load Book-Value Per Share data.
    if book_value:
        _load_book_value_per_share(ticker=ticker, df=df)

    # Load Dividend Per Share TTM data.
    if dividend_TTM:
        _load_dividend_TTM(ticker=ticker, df=df)

    return df


def load_stock_data(ticker, earnings=True, sales=True, book_value=True,
                    dividend_TTM=False):
    """
    Load data for a single stock from several different files
    and combine them into a single Pandas DataFrame.

    - Price is loaded from a Yahoo-file.
    - Other data is loaded from separate files.

    The Total Return is taken directly from the Yahoo price-data.
    Valuation ratios such as P/E and P/Sales are calculated daily
    from interpolated data.

    :param ticker:
        Name of the stock used in the filenames e.g. "WMT"

    :param earnings:
        Boolean whether to load data-file for Earnings Per Share.

    :param sales:
        Boolean whether to load data-file for Sales Per Share.

    :param book_value:
        Boolean whether to load data-file for Book-Value Per Share.

    :param dividend_TTM:
        Boolean whether to load data-file for Dividend Per Share TTM.

    :return: Pandas DataFrame with the data.
    """
    # Load the data-files.
    price_daily = _load_price_yahoo(ticker=ticker)

    # Use the DataFrame for the price and add more data-columns to it.
    df = price_daily

    # Only keep the rows where the share-price is defined.
    df.dropna(subset=[SHARE_PRICE], inplace=True)

    # Load Sales Per Share data.
    if sales:
        _load_sales_per_share(ticker=ticker, df=df)

    # Load Earnings Per Share data.
    # This needs the Sales Per Share data to calculate the profit margin.
    if earnings:
        _load_earnings_per_share(ticker=ticker, df=df)

    # Load Book-Value Per Share data.
    if book_value:
        _load_book_value_per_share(ticker=ticker, df=df)

    # Load Dividend Per Share TTM data.
    if dividend_TTM:
        _load_dividend_TTM(ticker=ticker, df=df)

    return df


def common_period(dfs):
    """
    Get the common start-date and end-date for the given DataFrames.

    :param dfs: List of Pandas DataFrames.
    :return: start_date, end_date
    """

    # Get all the start- and end-dates.
    start_dates = [df.index[0] for df in dfs]
    end_dates = [df.index[-1] for df in dfs]

    # Get the common start- and end-dates.
    common_start_date = np.max(start_dates)
    common_end_date = np.min(end_dates)

    return common_start_date, common_end_date


########################################################################
# Download and load data from Alpha Vantage www.alphavantage.co

# API key for Alpha Vantage.
_api_key_av = None


def set_api_key_av(api_key):
    """
    Set the API key for Alpha Vantage.

    :param api_key: String with the API key.
    :return: `None`
    """
    global _api_key_av
    _api_key_av = api_key


def load_api_key_av(path='~/alphavantage_api_key.txt'):
    """
    Load the API key for Alpha Vantage from the text-file with the given path.

    :param path: String with the path for the text-file.
    :return: `None`
    """
    # Expand the path if it begins with ~ for the user's home-dir.
    path = os.path.expanduser(path)

    # Read the first line from the file.
    with open(path) as f:
        key = f.readline().strip()

    # Set the API key for later use.
    set_api_key_av(api_key=key)


def _path_shareprices_intraday(ticker, interval):
    """
    Return the path for the CSV data-file with intra-day share-prices for the
    given stock-ticker and interval.

    :param ticker:
        String with the stock-ticker.

    :param interval:
        String with the data-interval: '1min', '5min', '15min', '30min', '60min'

    :return:
        String with the path for the CSV data-file.
    """

    # Filename and path for the data-file.
    filename = f'{ticker} Share-Price Intraday {interval} (AlphaVantage).csv'
    path = os.path.join(data_dir_intraday, filename)

    return path


def download_shareprices_intraday(tickers, interval, sleep=True):
    """
    Download intraday share-prices in CSV format from Alpha Vantage
    and save them as CSV-files in the data-directory.

    :param tickers:
        List of strings with stock-tickers, or just a single string.

    :param interval:
        String with the data-interval: '1min', '5min', '15min', '30min', '60min'

    :param sleep:
        Boolean whether to sleep after downloading data for each stock.
        AlphaVantage only allows 5 API calls per minute for free accounts.

    :return:
        `None`
    """

    assert _api_key_av is not None, 'You need to set an API key for Alpha Vantage'

    # If there is only a single ticker, convert it to a list.
    if not isinstance(tickers, list):
        tickers = [tickers]

    # Number of tickers.
    num_tickers = len(tickers)

    # Check if the data-directory exists, otherwise create it.
    if not os.path.exists(data_dir_intraday):
        os.makedirs(data_dir_intraday)

    # For all tickers.
    for i, ticker in enumerate(tickers):
        # Print status.
        msg = f'- Downloading {interval} share-prices for {ticker} ... '
        print(msg, end='')

        # Internet URL for the CSV-data.
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval={interval}&adjusted=True&outputsize=full&datatype=csv&apikey={_api_key_av}"

        # Path where the data-file should be saved.
        path = _path_shareprices_intraday(ticker=ticker, interval=interval)

        # Open a connection to the web-server.
        response = requests.get(url)

        # If connection is OK then download the contents.
        if response.status_code == 200:
            # Create local file and copy data from the server.
            with open(path, 'wb') as file:
                file.write(response.content)

            # Print status.
            print('Done!')
        else:
            # An error occurred so print the status-code.
            print(f'Error {response.status_code}')

        # The free Alpha Vantage accounts only allow 5 API calls per minute.
        # We could measure the time more accurately, but this sleep should
        # be sufficient. There is no need to sleep after the last ticker.
        if sleep and i < num_tickers - 1:
            time.sleep(13)


def load_shareprices_intraday(tickers, interval):
    """
    Load intraday share-prices from CSV-files in the data-directory.

    The returned DataFrame has a MultiIndex so each row is indexed by both
    a ticker and a time-stamp. This is because there may be different
    time-stamps available for each ticker. You can convert it to a DataFrame
    where the columns are tickers. For example, to get the CLOSE values from
    the returned DataFrame `df` we would call: `df[CLOSE].unstack().T`

    :param tickers:
        List of strings with stock-tickers, or just a single string.

    :param interval:
        String with the data-interval: '1min', '5min', '15min', '30min', '60min'

    :return:
        Pandas DataFrame.
    """
    # If there is only a single ticker, convert it to a list.
    if not isinstance(tickers, list):
        tickers = [tickers]

    # Dictionary with the resulting DataFrames for each ticker.
    df_dict = {}

    # For all tickers.
    for ticker in tickers:
        try:
            # Path for the CSV data-file.
            path = _path_shareprices_intraday(ticker=ticker, interval=interval)

            # Load CSV-file and set the correct index-column.
            df = pd.read_csv(path, sep=',', index_col='timestamp', parse_dates=True)

            # Rename index and columns.
            df.index.name = DATE_TIME
            new_names_map = \
                {
                    'open': OPEN,
                    'close': CLOSE,
                    'high': HIGH,
                    'low': LOW,
                    'volume': VOLUME
                }
            df.rename(columns=new_names_map, inplace=True)

            # Save the data in a dict for later use.
            df_dict[ticker] = df
        except:
            # An error occurred so we just skip that ticker.
            pass

    # Combine the data into a single Pandas DataFrame.
    df = pd.concat(df_dict, keys=df_dict.keys(), axis=0)

    return df


########################################################################
