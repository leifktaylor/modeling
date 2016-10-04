import re
import logging
import logboss as lb
import pandas as pd
import os
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.max_rows', 500000)
current_df = ''
current_type = ''
current_ds = ''

# TODO: Create logchecker class that stores line_list of entire log
# This way each command won't have to parse the file every single time it is invoked.


def help():
    print(bcolors.BOLD + 'HELP:')
    print(bcolors.OKBLUE + "grep('filename.log', 'substring', 'another...', ....) <-- try grep('-h')")
    print(bcolors.FAIL + "combine(dataframe1, dataframe2) <-- combines two dataframes")
    print(bcolors.OKGREEN + "save() <--- Saves current dataframe to csv")
    print(bcolors.WARNING + "load('file.csv') <--- Loads csv into dataframe")
    print(bcolors.ENDC + "ls() <-- view logs and csv in current directory")


def load(csv_file):
    """
    Opens csv file of actifio log files and converts to dataframe.
    :param csv_file: e.g. uddpmstuff.csv
    :return: dataframe object
    """
    global current_df
    log_dataframe = pd.read_csv(csv_file, dtype='str')
    log_dataframe.index = pd.to_datetime(log_dataframe.pop('date_time'), format='%Y-%m-%d %H:%M:%S.%f')
    current_df = log_dataframe
    return log_dataframe


def save(filename='savedataframe.csv'):
    """
    Saves most recently grepped dataframe to csv
    :param filename: output filename
    :return:
    """
    print("How to use save():")
    print("First grep to create a dataframe, or use combine to combine two dataframes")
    print("save() will save the last grepped, or the last combined dataframe to a csv")
    print("save('filename.csv') will save to the given outputfile.")

    global current_df
    try:
        dataframeobject = current_df
        dataframeobject.to_csv(filename)
        os.system('open {0}'.format(filename))
    except AttributeError:
        print('Must use "grep" to create a dataframe before you can save')


def create_datastructure(log_file, *args):
    """
    Creates a datastructure from a log file.
    Optional args allow grepping for only lines which contain args.

    :param args: words to grep for.
    :param log_file: specify log file so that lines can be parsed. e.g. 'uddpm.log' or 'UDSAgent.log'
    :return: pretty print on your screen!
    """
    line_list = read_lines_from_log(log_file, *args)
    log_datastructure = lb.read_log_line_list_to_data_structure(line_list, log_file)
    return log_datastructure


def combine(df1, df2, truncate=True):
    """
    Combines two dataframe objects together horizontally.

    :param df1: dataframe object
    :param df2: dataframe object
    :param truncate: show only timestamp and messages (enabled by default)
    :return: concatenated dataframe object
    """
    global current_df
    print("Combine(dataframe1, dataframe2)")
    print('Combine to dataframes. Create dataframe objects with "grep" and then combine')
    if truncate:
        combined_df = pd.concat([df1['message'], df2['message']], axis=1)
    else:
        combined_df = pd.concat([df1, df2], axis=1)
    current_df = combined_df
    return combined_df


def grep(filename, *args, **kwargs):
    """
    Prints lines from log file.  If substrings are given as args, prints only lines
    from file which contain those substrings.
    :param filename: log file to parse through
    :param args:
    :param kwargs: Optional: csv='filename' . to Write output to a CSV
    :return: Pandas dataframe object
    """
    global current_df
    global current_type
    if filename == '-h':
        print('Prints lines from log file.  If substrings are given as args, prints only lines')
        print('from file which contain those substrings.')
        print("e.g. grep('udppm.log', 'fail')")
        print("If grepping hundreds of thousands of rows, try csv='filename.csv>'")
        print('  This will save the query directly to a csv')
        print('')
        print("grep() also returns a dataframe object. set r = grep('udppm.log') to test.")
    print('-h for help')
    current_type = filename

    # Create datastructure (list of dicts) from lines in given log file (can only parse udppm and UDSagent currently)
    line_data = create_datastructure(filename, *args)

    # Create data frame from datastructured log lines (list of dictionaries)
    log_dataframe = pd.DataFrame(line_data)
    try:
        # Set dataframe index to time_index from 'date_time' column
        log_dataframe.index = pd.to_datetime(log_dataframe.pop('date_time'), format='%Y-%m-%d %H:%M:%S.%f')
    except KeyError:
        return 'No results found in query'
    cols = ['log_level', 'job_name', 'job', 'status', 'progress', 'message']
    current_df = log_dataframe[cols]
    if 'csv' in kwargs:
        log_dataframe[cols].to_csv(kwargs['csv'])
        os.system('open {0}'.format(kwargs['csv']))
        return 'saved CSV to {0}'.format(kwargs['csv'])
    return log_dataframe[cols]


def read_lines_from_log(filename, *args):
    """
    Opens a log or any file and returns a list of lines.
    If substring(s) are given as arguments, returns a list only the lines which contain either of the substring(s).

    :param filename: file to read from
    :param substring: substring to search for, if left blank, returns all lines.
    :param args: additional substrings to search for
    :return: list of lines

    """
    final_list = []
    # opens the file and reads lines into a list
    with open(filename, 'r') as log:
        for line in log:
            if args:
                # if any of the argument substrings in line
                for argument in args:
                    if argument in line:
                        final_list.append(line)
            # if no arguments given, just return all lines
            else:
                final_list.append(line)
        log.close()
    return final_list


# **** convenience
class bcolors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def ls():
    print(bcolors.OKBLUE + "CSV Files:")
    os.system('ls *.csv')
    print(bcolors.OKGREEN + "log Files:")
    os.system('ls *.log')
    print(bcolors.ENDC)





# ************* Log datastructure queries
# TODO: Place in different module
