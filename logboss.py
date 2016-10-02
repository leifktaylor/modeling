#!/usr/bin/env python
import re
import csv
import os
import json
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib
import argparse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')
pd.set_option('display.width', 999)
pd.set_option('display.max_colwidth', 100)


# TODO: Plot numerical data, plot and compare.
# TODO: Gather all logs (udppm, psrv, UDSAgent)
# TODO: Combine logs

# logstash (framework)

# Be able to pull UDSAgent, pserv, udppm.  Combine them all together in a dataframe and
# be able to view them side by side.

# 2016-09-30 16:11:06.979 INFO   Job_3672360:

# udppm log parsing *****
# TODO: udsagent parser!!!

def determine_line_type(line):
    # Determine if the line type fits a particular template
    if 'job=' and 'message=' and 'progress=' and 'status=' in line:
        return (read_jobstatus_line(line))
    return None


def read_jobstatus_line(line):
    # parse a line for jobstatus info and place into dictionary
    item_list = ['job', 'message', 'progress', 'status']
    job_status = {}
    for item in item_list:
        if item not in line:
            item_list.pop(item)
        else:
            try:
                job_status[item] = re.search('{0}="(.*?)"'.format(item), line).group(1).strip(':')
            except AttributeError:
                print('element not found')

    # add date information
    job_status['date_time'] = '{0} {1}'.format(line.split()[0], line.split()[1])
    # add log level
    job_status['log_level'] = '{0}'.format(line.split()[2])
    # add job name
    job_status['job_name'] = line.split()[3].strip(':')
    return job_status


def read_log_lines_to_list(log_file):
    # Open file for reading
    with open(log_file, 'r') as file:
        content = file.readlines()
        file.close()
    return content


def read_log_line_list_to_data_structure(line_list):
    main_list = []
    for line in line_list:
        r = determine_line_type(line)
        if r:
            main_list.append(r)
    return main_list


# JSON Handling *****

def write_log_to_json(filename, loglist, write_type='w'):
    """
    Populates file with log data in json format.
    :param filename: output file
    :param loglist: list of lines from logfile
    :param write_type: 'w' (overwrite) or 'a' (append)
    :return:
    """
    with open(filename, 'w') as outputfile:
        json.dump(loglist, outputfile)
        outputfile.close()
    print('Json data written to {0}'.format(filename))

# CSV Handling *****


def populate_log_csv(log_type='udppm', log_list, write_type='w'):
    # TODO: Improve time stamping in ingest
    """
    Populates CSV from list of log lines.

    :param log_list: list of log lines.
    :param write_type: 'w' (overwrite) or 'a' (append)
    :param log_type: 'udppm' or 'udsagent'
    :return:
    """
    # Create a CSV if one doesn't exist
    if not file_exists(log_type):
        create_csv(log_type+'.csv')

    if log_type == 'udppm':
        # Create list from log_list
        log_lines = []
        for dict in log_list:
            current_line = []
            order_key = {'date_time': 1, 'log_level': 2, 'job_name': 3, 'status': 4,
                         'job': 5, 'progress': 6, 'message': 7}
            for item in sorted(dict, key=order_key.__getitem__):
                current_line.append(dict[item])
            log_lines.append(current_line)

        # Write into CSV
        with open(filename, write_type) as log_csv:
            wr = csv.writer(log_csv, quoting=csv.QUOTE_ALL)

            # Write header row
            wr.writerow(['date_time', 'log_level', 'job_name',
                         'status', 'job', 'progress', 'message'])

            # Write log data
            for line in log_lines:
                wr.writerow(line)
        log_csv.close()
    elif log_type == 'udsagent':
        # Create list from log_list
        log_lines = []
        for dict in log_list:
            current_line = []
            order_key = {'date_time': 1, 'log_level': 2, 'job_name': 3, 'status': 4,
                         'job': 5, 'progress': 6, 'message': 7}
            for item in sorted(dict, key=order_key.__getitem__):
                current_line.append(dict[item])
            log_lines.append(current_line)

        # Write into CSV
        with open(filename, write_type) as log_csv:
            wr = csv.writer(log_csv, quoting=csv.QUOTE_ALL)

            # Write header row
            wr.writerow(['date_time', 'log_level', 'job_name',
                         'status', 'job', 'progress', 'message'])

            # Write log data
            for line in log_lines:
                wr.writerow(line)
        log_csv.close()


    else:
        print('Invalid log type. Accepts "udppm" or "udsagent"')

    print('{0} spreadsheet updated'.format(log_type+'.csv'))


def create_csv(filename):
    """
    Creates a csv file.
    :return: filename
    """
    new_csv = open(filename, 'wb')
    new_csv.close()
    return filename

# Matplotlib Graphing



# Pandas Dataframe Handling ****


class LogDataframe(object):
    def __init__(self, dataframe, print_all=False):
        """
        :param dataframe:
        :param print_all: print_all will print all queries to the screen in addition to creating dataframe objects
        """
        self.df = dataframe
        self.print_all = print_all

    def select(self, column_name, value, spawn_csv=False):
        """
        Select from 'column_name' where item == 'value'.

        :param column_name: column name to query
        :param value: value of row in column
        :param dataframe: pandas dataframe object
        :return:
        """
        dataframe = self.df
        query = dataframe.loc[dataframe[column_name] == value]
        return query

    def show(self, **kwargs):
        """
        #TODO: Make 'has'
        Pretty prints a dataframe, can add arguments.
        :param column: column header string
        :param value: row value
        :param has: row value string has 'X' in it.
        :param t1: start time (requires t2)
        :param t2: end time (requires t1)
        :param messages: show status messages only (set to True)
        :return: dataframe object
        """
        col_width = 100
        if 'column' in kwargs:
            if 'value' in kwargs and 'has' in kwargs:
                print('CANNOT SHOW DATAFRAME. Choose either "value" or "has", not both.')
            elif 'value' in kwargs:
                print('QUERIED')
                dataframe_object = self.select(kwargs['column'], kwargs['value'])
            elif 'has' in kwargs:
                dataframe_object = self.df[self.df[kwargs['column']].str.contains(kwargs['has'])]
            else:
                print('Include a "value" or a "has" along with the "column"')
        else:
            dataframe_object = self.df
        if 't1' and 't2' in kwargs:
            dataframe_object = dataframe_object.loc[kwargs['t1']:kwargs['t2']]
        if 'messages' in kwargs:
            dataframe_object = dataframe_object[['job_name', 'message']]
            col_width = 100
        pd.set_option('display.max_colwidth', col_width)
        pd.set_option('display.max_rows', len(dataframe_object))
        print(dataframe_object)
        pd.reset_option('display.max_rows')
        pd.set_option('display.max_colwidth', 100)
        # GUI Guide
        print('Column names: ' + str(list(dataframe_object.columns.values)))
        print('SELECT:')
        # print("show()  <--- Show entire Dataframe")
        # print("show( column='something', value='row value' ) ")
        # print("show( column='something', has='some substring' ")
        # print("show( dataframe='data_frame_object' )")
        print('logboss -c job_name -r Job_12345  <--- select rows for exact value')
        print('logboss -c message -s "failed to"   <--- select for substring match')
        print('logboss -m True         <--- log messages only')
        print('logboss -t1 "2016-09-11 17" -t2 "2016-09-11 18"  <--- select within time')
        print('logboss -h (for help)')

    def spawn_dataframe_from_jobname(self, jobname):
        """
        Creates a dataframe object from the given jobname

        e.g.
        dataframe = create_dataframe_from_jobname('Job_12345')

        :param jobname: e.g. 'Job_12345'
        :return: dataframe object
        """
        dataframe_object = self.df
        dataframe = dataframe_object.loc[dataframe_object['job_name'] == jobname]
        if self.print_all:
            self.print_dataframe(dataframe)
        return dataframe

    def spawn_dataframe_from_loglevel(self, loglevel, dataframe_object=''):
        """
        Creates a dataframe containing only rows of given loglevel.

        :param loglevel: e.g. 'INFO', or 'DEBUG', or 'SEVERE'
        :return: dataframe object
        """
        if not dataframe_object:
            dataframe_object = self.df
        dataframe = dataframe_object.loc[dataframe_object['log_level'] == loglevel.upper()]
        if self.print_all:
            self.print_dataframe(dataframe)
        return dataframe

    def spawn_dataframe_within_time(self, t1, t2, dataframe_object=''):
        # TODO: Make this work
        """
        Creates a dataframe containinly rows between two given times
        :param t1: 'YYYY-MM-DD HR:MN:SC'
        :param t2: 'YYYY-MM-DD HR:MN:SC'
        :return: dataframe object
        """
        # if not dataframe_object:
        #     dataframe_object = self.df
        dataframe = dataframe_object.loc[t1:t2]
        if self.print_all:
            self.print_dataframe(dataframe)
        return dataframe


def create_dataframe_from_csv(csv_file):
    """
    Creates a LogDataframe class instantiation with a dataframe object as attribute.
    :param csv_file: input csv file.
    :return:
    """
    # INIT -----
    log_dataframe = pd.read_csv(csv_file, dtype='str')
    log_dataframe.index = pd.to_datetime(log_dataframe.pop('date_time'), format='%Y-%m-%d %H:%M:%S.%f')
    #log_dataframe.index = pd.to_datetime(log_dataframe.pop('date_time'), nfer_datetime_format=True)

    #log_dataframe['date_time'] = pd.to_datetime(log_dataframe['date_time'])
    #log_dataframe['date_time'] = pd.date_range('2000-1-1', periods=200, freq='D')
    #log_dataframe = log_dataframe.set_index(['date_time'])
    #print('Issue with source {0}'.format(csv_file))
    return LogDataframe(log_dataframe)


def combine_dataframes(self, dataframe1, dataframe2):
    """
    Combines two dataframes.

    :param dataframe1:
    :param dataframe2:
    :return: concatenated dataframe
    """
    return pd.concat(dict(df1=dataframe1, df2=dataframe2), axis=1)

# Utility ****


def file_exists(filename):
    """
    Checks if given file exists

    :param filename: file to check for
    :return: True if file exists, False if not
    """
    return os.path.isfile(filename)


def run_test(**kwargs):
    """
    Puts job related udppm log data into a datastructure.
    jobname='blah' for only a specific job
    :return:
    """
    content = read_log_lines_to_list('udppm.log')
    main_list = read_log_line_list_to_data_structure(content)
    final_list = []
    if 'jobname' in kwargs:
        for item in main_list:
            if kwargs['jobname'] == item['job_name']:
                final_list.append(item)
    else:
        final_list = main_list
    #for item in final_list:
    #    print(item)
    # Write to Json
    write_log_to_json('udppm.json', final_list)
    # Write to CSV
    populate_log_csv('udppm', final_list)
    # Create Dataframe Object
    return create_dataframe_from_csv('logtest.csv')


def parseArguments():
    """
    Parses arguments given at commandline.
    :return:
    """
    parser = argparse.ArgumentParser()
    #Optional Ar
    parser.add_argument("-c", "--column", help="select from this column.", default='')
    parser.add_argument("-r", "--row", help="an exact row value.", default='')
    parser.add_argument("-s", "--substring", help="rows that contain this substring", default='')
    parser.add_argument("-m", "--messages", help="status message only", default='')
    parser.add_argument("-t1", "--time1", help="start time (get rows in range t1-t2)", default='')
    parser.add_argument("-t2", "--time2", help="end time (get rows in range t1-t2)", default='')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # Get arguments
    args = parseArguments()
    column = str(args.column)
    row = str(args.row)
    substring = str(args.substring)
    t1 = str(args.time1)
    t2 = str(args.time2)
    messages = str(args.messages)

    # Prepare KW Args for show function
    kwargs = {}
    if column:
        kwargs['column'] = column
    if row:
        kwargs['value'] = row
    if substring:
        kwargs['has'] = substring
    if t1 and t2:
        kwargs['t1'] = t1
        kwargs['t2'] = t2
    if messages:
        kwargs['messages'] = messages

    # Create Dataframe
    a = run_test()
    a.show(**kwargs)

        # TODO: Plot numerical data of:
        # Length of backup jobs compared to other backup jobs
        # Length of
        # df = a.df.cumsum()
        # plt.figure();
        # df.plot();
