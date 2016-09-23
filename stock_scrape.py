"""
STOCKS
Author: Leif Taylor , Sep 2016
"""

from bs4 import BeautifulSoup
import requests
import re
import json
import urllib2
import urlparse
import os
import platform
import ctypes
import sys
import mimetypes
import shutil
import datetime
import glob
import locale
import csv
import threading
import thread
import time
from Queue import Queue
import __future__

# TODO: list_market_stocks   . Finish this function and make it readable
# TODO: Integrate with QuickFix python api for automated trading, or mechanize fidelity
# TODO: Factor in commission for sales and purchases
# TODO: Save account object for later loading
#       save_list = [ self.balance, [{stock: shares}. {stock: shares}, ... ] ]
#       list with dictionary of Stocks and shares
# TODO: Make function that instantiates n Accounts, saves IDs to spreadsheet
# TODO: Make login() takes id from accounts spreadsheet
# TODO: Make function that stores account balance/trading info into database
# TODO: Record trades into account info
# TODO: Make behaviors template (trade stock if)
# TODO: Automate ingests at x time
# TODO: Round Robin for stock ingest
# TODO: Method that writes Account.history to csv
# TODO: Use Keras for deep learning
# TODO: Fix timestamping on market ingest


class Account(object):
    """
    Account object can trade in securities.
    Security valuation data is scraped from Yahoo Finance.
    To generate a 'stock_data_file' use 'update_market_data'

    Account data is stored in self.portfolio
    """
    def __init__(self, balance, name='Leif', commission=8.00, stock_data_file='', history_file='trade_hist.csv'):
        self.balance = balance
        self.commission = commission
        self.stock_data_file = stock_data_file
        self.name = name
        self.portfolio = [{'STOCK': 0.0}]
        self.history = []
        self.history_file = history_file

    def buy_shares(self, symbol, shares):
        """
        Buys shares of a particular stock

        :param symbol: ticker symbol, e.g. AERI
        :param shares: how many shares to purchase
        :return:
        """

        # Load all external stock data and calculate price
        if self.stock_data_file != '':
            try:
                stock_dict = open_stock_data(self.stock_data_file)
            except IOError:
                print('Could not load stock data file: {0}'.format(self.stock_data_file))
                stock_dict = {}
        if not get_live_price(symbol):
            print('Symbol not found')
            return 1
        try:
            stock_price = get_live_price(symbol)
            total_cost = float(stock_price) * shares

            # determine if sufficient funds
            if self.balance - total_cost >= 0:
                self.balance -= total_cost
                # check if stock already in portfolio
                in_port = False
                for stock in self.portfolio:
                    if symbol in stock:
                        in_port = True
                        port_index = self.portfolio.index(stock)

                # append to portfolio
                if in_port:
                    self.portfolio[port_index][symbol] += shares
                else:
                    self.portfolio.append({symbol: shares})

                print('Purchased {0} shares of {1} for {2}'.format(shares, symbol, p_money(total_cost)))
                print('Remaining account balance: {0}'.format(p_money(self.balance)))
            else:
                print('Insufficient Funds.  Cost of {0} shares is {1}'.format(shares, p_money(total_cost)))
                print('Account Balance: {0}'.format(p_money(self.balance)))

            # append transaction data to self.history
            self.record_transaction(symbol, shares, 'buy')

        # Stock is not listed in market dictionary
        except KeyError:
            print('Stock {0} is not listed.'.format(symbol))

    def sell_shares(self, symbol, shares):
        # Load all external stock data and calculate price
        if self.stock_data_file != '':
            try:
                stock_dict = open_stock_data(self.stock_data_file)
            except IOError:
                print('Could not load stock data file: {0}'.format(self.stock_data_file))
                stock_dict = {}
        try:
            stock_price = get_live_price(symbol)
            total_sale = float(stock_price) * shares

            # determine if sufficient shares and sell
            if shares <= self.find_shares_in_portfolio(symbol):
                port_index = self.find_portfolio_index(symbol)
                self.portfolio[port_index][symbol] -= shares
                self.balance += total_sale
                print('Sold {0} shares of {1} for a total of {2}'.format(shares, symbol, p_money(total_sale)))
            else:
                # if insufficient shares
                print('Failed')
                print('Cannot sell {0} shares because you only have {1}'.format(shares,
                                                                                self.find_shares_in_portfolio(symbol)))

            # append transaction data to self.history
            self.record_transaction(symbol, shares, 'sell')

        # if stock isn't in portfolio
        except KeyError:
            print('Stock {0} is not listed.'.format(symbol))
        pass

    def find_shares_in_portfolio(self, symbol):
        """
        Checks to see if stock is in portfolio and returns the amount of
        shares of that stock.
        Returns none if not in portfolio.

        :return: amount of shares
        """
        shares = ''
        for stock in self.portfolio:
            for key in stock:
                if key == symbol:
                   shares = stock[key]
        return shares

    def find_portfolio_index(self, symbol):
        """
        Returns the index from the given symbol.
        If the stock is not in the portfolio returns none.

        :param symbol: ticker symbol. e.g. ATVI
        :return: portfolio index (portfolio is a list)
        """
        portfolio_index = ''
        for stock in self.portfolio:
            for key in stock:
                if key == symbol:
                    portfolio_index = self.portfolio.index(stock)
        return portfolio_index

    def print_portfolio(self):
        """
        Prints out Account holder portfolio information including stocks owned,
        account balance, and total value of securities.

        :return:
        """
        if self.stock_data_file:
            stock_dict = open_stock_data(self.stock_data_file)
        symbol_list = []
        total_stock = 0
        for stock in self.portfolio:
            for key in stock:
                if key == 'STOCK':
                    print('Symbol   |Shares     |Per Share  |Total')
                else:
                    symbol_list.append(key)
                    stock_price = get_live_price(key)
                    total_value = (float(stock_price) * float(stock[key]))
                    total_stock += total_value

                    print('{0}      |{1}        |{2}       |{3}'.format(key, stock[key],
                                                                        p_money(stock_price), p_money(total_value)))
        print('Total Stock:   {0}'.format(p_money(total_stock)))
        print('Cash Balance:  {0}'.format(p_money(self.balance)))
        print('Total Worth:   {0}'.format(p_money(self.balance + total_stock)))

    def print_history(self):
        print('Sales History\n')
        print('DATE TIME  | TYPE | SHARES | TOTAL SALE | PPS   | BALANCE   | SYMBOL ')
        for sale in self.history:
            print(sale['DATETIME'], sale['TYPE'], sale['TRANSACTIONSHARES'], p_money(sale['TOTALSALE']),
                  p_money(sale['PPS']), p_money(sale['BALANCE']), sale['SYMBOL'])


    def list_market_stocks(self):
        #TODO: Finish this
        """
        Lists stocks and prices from stock_file.  Note these prices
        are only as up to date as the time_stamp on the data_file assosciated
        with the account.

        :return:
        """
        counter = 0
        # Open stock data file to a list of dictionaries

        # Display them in human readable way across the screen
        #for stock in
        pass

# ****** Trade History

    def record_transaction(self, symbol, shares, sale_type):
        """
        Records purchase of shares into self.history list

        :param symbol: stock ticker, e.g. ATVI
        :param shares: number of shares
        :param sale_type: 'buy' or 'sell'
        :return:
        """
        if sale_type not in ['buy', 'sell']:
            print('Unknown sale type.  Accepted: "buy" or "sell"')
        else:
            # Get data from transaction
            trader = self.name
            stock_symbol = symbol
            price_per_share = get_live_price(symbol)
            date_time = get_date_time()
            transaction_shares = shares
            sale_type = sale_type
            account_balance = self.balance
            #TODO: IMPLEMENT COMMISSION HERE
            total_sale = price_per_share * transaction_shares
            total_shares = self.find_shares_in_portfolio(symbol)

            # append to self.history list
            self.history.append({'NAME': trader, 'PPS': price_per_share, 'DATETIME': date_time,
                                 'TOTALSHARES': total_shares, 'TRANSACTIONSHARES': transaction_shares,
                                 'SYMBOL': stock_symbol, 'TYPE': sale_type, 'TOTALSALE': total_sale,
                                 'BALANCE': account_balance})


# ****** ACCOUNT HANDLING


def apply_updated_market_data(account, data_file):
    """
    Applies market data_file to account.
    This file can be generated with update_market_data()

    :param account: account object instance
    :param data_file: stock data file
    :return:
    """
    account.stock_data_file = data_file


def list_market_data_files():
    print('Nasdaq Data Files:')
    print(glob.glob('NASD_Listings_*'))
    print('\n')
    print('Other Listed Data Files: ')
    print(glob.glob('otherl*'))


def update_market_data():
    """
    Updates market listings for NYSE.  Can be applied to Account.

    :return: stock_data_file path for Account object
    """
    # Download files from Nasdaq FTP
    nasdaqlist, otherlisted = download_latest_nyse_data()
    # Parse file for Symbols
    raw_lines = open_nasdaq_symbol_file(nasdaqlist)
    symbol_list = parse_symbols_to_list(raw_lines)
    print('Downloading current stock values...')
    # Read all stock data from Yahoo Finance using Symbols
    stock_dict = read_yahoo_stocks(symbol_list)
    # Output Yahoo Finance stock data into stock data_file.
    data_file = save_stock_dictionary_to_file(stock_dict, 'NASD_Listings_' + str(get_approx_time()))
    return data_file


def load_account_from_file(filename):
    """
    Loads account data from file

    :param filename: filename to load
    :return: list of dictionaries with account data
    """
    pass


# ****** Nasdaq/FTP Sourcing


def download_latest_nyse_data():
    """
    Downloads latest nasdaqlist.txt and otherlisted.txt from:
    ftp://ftp.nasdaqtrader.com/SymbolDirectory/

    :return: nasdaqlisted.txt filename, otherlisted.txt filename
    """
    # TODO: Write this function
    nasdaqlistedname = 'nasdaqlisted_'+str(get_approx_time())+'.txt'
    otherlistedname = 'otherlisted_'+str(get_approx_time())+'.txt'
    download_file_locally('ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt', nasdaqlistedname)
    download_file_locally('ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt', otherlistedname)
    print('Downloaded list of symbols from Nasdaq')
    return nasdaqlistedname, otherlistedname


def open_nasdaq_symbol_file(filename):
    """
    Opens nasdq file and places elements into a list
     # ftp://ftp.nasdaqtrader.com/SymbolDirectory/
    two files to search are:
    # otherlisted.txt, and nasdaqlisted.txt
    :param filename: nasdaq symbol list test file
    :return: list of lines
    """
    try:
        with open(filename) as f:
            line_list = f.readlines()
        f.close()
        return line_list
    except IOError:
        print('Could not find {0}. Does it exist?'.format(filename))
        raise


def open_stock_data(filename):
    """
    Opens stock data file generated from save_stock_dictionary_to_file.
    Returns a list of dictionaries

    :param filename: data file path
    :return: list of dictionaries with stock data
    """
    try:
        with open(filename, 'r') as data_file_object:
            stock_dictionary = json.load(data_file_object)
        data_file_object.close()
        return stock_dictionary
    except IOError:
        print('Unable to open stockfile: {0}'.format(filename))
        return {}


def parse_symbols_to_list(nasdaq_list):
    """
    Parses list generated from nasdaq file. file from:

    :param nasdaq_list: list of lines from nasdaq.txt file
    :return: list of symbols
    """
    symbol_list = []
    for line in nasdaq_list:
        symbol_list.append(line.partition('|')[0])
    return symbol_list


# ****** FTP / HTTPS HANDLING


def filename_from_url(url):
    return os.path.basename(urlparse.urlsplit(url)[2])


def download_file(url):
    """
    Create ftp requests using input URL

    :param url: url of file to download
    :return:
    """
    name = filename_from_url(url)
    r = urllib2.urlopen(urllib2.Request(url))
    info = r.info()
    if 'Content-Disposition' in info:
        # If the response has Content-Disposition, we take filename from it
        name = info['Content-Disposition'].split('filename=')[1]
        if name[0] == '"' or name[0] == "'":
            name = name[1:-1]
    elif r.geturl() != url:
        # if we were redirected, take the filename from the final url
        name = filename_from_url(r.geturl())
    content_type = None
    if 'Content-Type' in info:
        content_type = info['Content-Type'].split(';')[0]
    # Try to guess missing info
    if not name and not content_type:
        name = 'unknown'
    elif not name:
        name = 'unknown' + mimetypes.guess_extension(content_type) or ''
    elif not content_type:
        content_type = mimetypes.guess_type(name)[0]
    return r, name, content_type


def download_file_locally(url, dest):
    req, filename, content_type = download_file(url)
    if dest.endswith('/'):
        dest = os.path.join(dest, filename)
    with open(dest, 'wb') as f:
        shutil.copyfileobj(req, f)
    req.close()
    return filename


# ******* YAHOO STOCK API

def setup_queue(symbol_list):
    """
    Determines total amount of threads needed for market ingest
    and creates queue.

    :param symbol_list: list of market tickers, e.g. ATVI
    :return:
    """
    # init queue
    q = Queue(maxsize=0)

    # load up queue
    for i in range(len(symbol_list)):
        q.put((i, symbol_list[i]))
    return q


def multithread_ingest(q):
    """
    Uses queue to control threads.

    :param q: queue object
    :return:
    """
    while not q.empty():
        work = q.get()
        try:
            read_yahoo_stock(work[1], True, True)
        except:
            print('Thread error')
        # task completed
        q.task_done()
    return True


# global variable used for multi-threading
thread_results = {}


def read_yahoo_stocks(symbol_list, max_threads=32):
    """
    Reads all stocks from yahoo finance.
    Uses symbol_list of Tickers to query page by page.

    :param symbol_list: list of tickers, e.g. ATVI
    :param max_threads: maximum threads to use in multi-threading
    :return:
    """
    global thread_results
    thread_results = {}
    # set max threads to 30
    num_threads = min(max_threads, len(symbol_list))

    # Init queue
    q = setup_queue(symbol_list)

    results = {}

    for i in range(num_threads):
        worker = threading.Thread(target=multithread_ingest, args=(q, ))
        # allow program to continue eventually even if threads fail
        worker.setDaemon(True)
        worker.start()

    # wait until queue finished
    q.join()
    print('Threads converged. Ingest Completed')
    return thread_results


def save_stock_dictionary_to_file(stock_dict, filename):
    """
    Writes stock info dictionary to a file

    :param stock_dict: dictionary of stocks and information
    :param filename: file to output to
    :return: file name
    """
    # TODO: Generate dated file name
    with open(filename, 'w') as output_dictionary_file:
        json.dump(stock_dict, output_dictionary_file)
    output_dictionary_file.close()
    return filename


def read_yahoo_stock(stock_symbol, display=True, write_to_global=False):
    # TODO: Retrieve more values
    """
    Reads price from yahoo.com for given stock symbol.

    :param stock_symbol: e.g. AERI
    :return: symbol, and price
    """

    symbol = stock_symbol
    price = ''
    if symbol == '\n' or symbol == 'Symbol':
        if display:
            print('\n')
    else:
        url = 'http://finance.yahoo.com/q?s={}'.format(symbol)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        output = str(soup)
        try:
            result = re.search("\$price\.0\">(\d+)\.(\d+)", output)
            price = result.group(0).strip('$price.0">')
            if display:
                print('{0} = {1}'.format(symbol, price))
        except AttributeError:
            print("Unknown symbol or parsing is broken: {}".format(symbol))
            symbol, price = '', ''
        if write_to_global:
            # writes to global variable used for multithreading
            thread_results[symbol] = [price, get_date_time()]
        return symbol, price


def get_live_price(symbol):
    """
    Returns current actual price of a stock

    :param symbol: e.g. AERI
    :return: price in USD
    """
    r, price = read_yahoo_stock(symbol.upper(), False)
    if r == '':
        return ''
    else:
        return float(price)

# ******* UTILITY


def get_date_time():
    """
    :return: Time in Y-M-D H:M:S
    """
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return time


def get_approx_time():
    time = datetime.datetime.now().strftime("%m-%d_%H_%M")
    return time


def p_money(money):
    """
    Returns UDS amount with commas

    :param money: floating point cash amount
    :return: cash amount with commas
    """
    r = locale.currency(money, grouping=True)
    return r


def file_exists(filename):
    """
    Checks if given file exists

    :param filename: file to check for
    :return: True if file exists, False if not
    """
    return os.path.isfile(filename)


def split_list(a_list):
    """
    Split list in half

    :param a_list: list to split
    :return: list_half, list_other_half
    """
    half = len(a_list)/2
    return a_list[:half], a_list[half:]


def merge_two_dicts(x, y):
    """
    Merge two dictionaries.

    :param x: dictionary 1
    :param y: dictionary 2
    :return: merged dictionary
    """
    z = x.copy()
    z.update(y)
    return z

# ******* JSON Utility


def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return dict((_byteify(key, ignore_dicts=True),
                     _byteify(value, ignore_dicts=True)) for key, value in data.iteritems())

    # if it's anything else, return it in its original form
    return data


# ******* CSV Interaction

def create_csv(filename, *args):
    """
    Creates a csv file with the given name and column header names.

    :param args: List of column header names
    :param args: List of column header names
    :return: filename
    """
    new_csv = open(filename, 'wb')
    wr = csv.writer(new_csv, quoting=csv.QUOTE_ALL)
    wr.writerow(*args)
    new_csv.close()
    return filename


def populate_market_csv(filename, datafile):
    #TODO: Improve time stamping in ingest
    """
    Writes TICKER VALUE information to csv file.
    If csv does not already exist, creates one with
    header information and then populates.

    :param filename: filename to write to
    :param datafile: datafile created from 'update_market_data'
    :return:
    """
    if not file_exists(filename):
        create_csv(filename, ['TIME', 'SYMBOL', 'VALUE'])

    # Get stock {Ticker: Value} dictionary from datafile
    market_dict = open_stock_data(datafile)
    # Get timestamp from datafile
    time_stamp = datafile.strip('NASD_Listings_')

    # Create list of lists from data [time, symbol, value]
    stocks_list = []
    for key, value in sorted(market_dict.iteritems()):
        symbol = key
        values = value
        # remove unicode prepends
        string_values = []
        for item in values:
            #TODO: is strip needed?
            string_values.append(str(item).strip('u'))
        stocks_list.append([time_stamp, symbol, string_values])

    # Write into CSV
    with open(filename, 'a') as market_csv:
        wr = csv.writer(market_csv, quoting=csv.QUOTE_ALL)
        for stock in stocks_list:
            wr.writerow(stock)
    market_csv.close()

    print('{0} spreadsheet updated'.format(filename))


def populate_history_csv(filename, history):
    """
    Populates CSV with list sales transaction history of Account object.

    :param filename: output filename
    :param history: Account.history (list of dicts)
    :return:
    """
    # TODO: Write this method | populate_history_csv
    pass


# ******* CLI


def init_cli(account_object):
    #TODO: Searching stocks
    """
    Command-line interface for controlling account behaviors.

    Type HELP for a list of commands

    :param account_object: pointer to Account object.
    :return:
    """
    # set currency locale
    locale.setlocale(locale.LC_ALL, '')

    a = account_object
    valid_commands = ['help', 'search', 'buy', 'sell', 'stats', 'history', 'quit', 'update']
    print('REAL-TIME STOCK SIMULATOR:')
    print('Logged in as: {0}'.format(a.name))
    print('Type "help" for a list of commands')
    while True:
        choice = raw_input('@{0}: '.format(a.name))
        if choice not in valid_commands:
            print('Not a valid command.  Type "help" for a list of commands')
        else:
            if choice == 'help':
                print(valid_commands)

            if choice == 'quit':
                print('Logged out of {0}'.format(a.name))
                break

            if choice == 'stats':
                a.print_portfolio()

            if choice == 'buy':
                print('Balance: {0}'.format(p_money(a.balance)))
                symbol = raw_input('Stock to buy (SYMBOL): ')
                symbol = symbol.upper()
                if a.stock_data_file:
                    stock_dict = open_stock_data(a.stock_data_file)
                try:
                    stock_price = get_live_price(symbol)
                    print('Cost per share: {0}'.format(p_money(stock_price)))
                    shares = raw_input('Amount of shares: ')
                    total_cost = int(shares) * float(stock_price)
                    print('Total cost {0}, Continue? y/n'.format(p_money(total_cost)))
                    choice = raw_input()
                    if choice == 'y':
                        a.buy_shares(symbol, int(shares))
                    else:
                        print('Transaction canceled')
                except KeyError:
                    print('Stock not found')
                except TypeError:
                    print('Stock not found')

            if choice == 'sell':
                symbol = raw_input('Stock to sell (SYMBOL): ')
                symbol = symbol.upper()
                if a.stock_data_file:
                    stock_dict = open_stock_data(a.stock_data_file)
                try:
                    num_shares = a.find_shares_in_portfolio(symbol)
                    stock_price = get_live_price(symbol)
                    print('Shares: {0}'.format(num_shares))
                    print('Value per share: {0}'.format(p_money(stock_price)))
                    print('Total Position: {0}'.format(p_money(stock_price * num_shares)))
                    shares = raw_input('Number of shares to sell: ')
                    total_cost = int(shares) * float(stock_price)
                    print('Total cost {0}, Continue? y/n'.format(p_money(total_cost)))
                    choice = raw_input()
                    if choice == 'y':
                        a.sell_shares(symbol, int(shares))
                    else:
                        print('Transaction canceled')
                except KeyError:
                    print('Stock not found')
                except TypeError:
                    print('Stock not listed, or not owned')

            if choice == 'history':
                #TODO: Display csv.. somehow
                a.print_history()

            if choice == 'search':
                #TODO: Stock searching
                print('Search is offline')

            if choice == 'update':
                a.stock_data_file = update_market_data()
                populate_market_csv('market_csv.csv', a.stock_data_file)

            if choice == 'save':
                #TODO: Save account profile
                # Probably autosave will be enabled as well
                print('Save is offline')
            if choice == 'load':
                #TODO: Load account profile
                print('Load is offline')


# TODO: Append each stock to file one by one, rather than waiting for entire dictionary
# TODO: If interrupted, make resume option.

def download_list():
    the_list = open_nasdaq_symbol_file('nasdaqlisted.txt')
    symbol_list = parse_symbols_to_list(the_list)
    stock_dict = read_yahoo_stocks(symbol_list)
    save_stock_dictionary_to_file(stock_dict, 'dow_info.txt')
    return


def login(username='Leif', password='', balance='5000'):
    a = Account(5000, username)
    init_cli(a)


def repeated_ingest(delay=60, max_ingests=''):
    counter = 0
    while True:
        update_market_data()
        time.sleep(delay)
        if max_ingests:
            counter += 1
            if counter >= max_ingests:
                break

