import re
import csv
import os
import json
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib
pd.set_option('display.width', 999)
pd.set_option('display.max_colwidth', 100)

# logstash (framework)

# Be able to pull UDSAgent, pserv, udppm.  Combine them all together in a dataframe and
# be able to view them side by side.

# 2016-09-30 16:11:06.979 INFO   Job_3672360:


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


def populate_log_csv(filename, log_list, write_type='w'):
    # TODO: Improve time stamping in ingest
    """
    Populates CSV from list of log lines.

    :param filename: filename to write to
    :param log_list: list of log lines.
    :param write_type: 'w' (overwrite) or 'a' (append)
    :return:
    """
    # Create a CSV if one doesn't exist
    if not file_exists(filename):
        create_csv(filename)

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

    print('{0} spreadsheet updated'.format(filename))


def create_csv(filename):
    """
    Creates a csv file.
    :return: filename
    """
    new_csv = open(filename, 'wb')
    new_csv.close()
    return filename

# Pandas Dataframe Handling ****


class LogDataframe(object):
    def __init__(self, dataframe, print_all=True):
        """
        :param dataframe:
        :param print_all: print_all will print all queries to the screen in addition to creating dataframe objects
        """
        self.master_dataframe = dataframe
        self.print_all = print_all

    def print_dataframe(self, dataframe_object=''):
        """
        Pretty prints a dataframe
        :param dataframe_object: dataframe object to print
        :return:
        """
        dataframe_object = self.master_dataframe
        pd.set_option('display.max_rows', len(dataframe_object))
        print(dataframe_object)
        pd.reset_option('display.max_rows')

    def spawn_dataframe_from_jobname(self, jobname):
        """
        Creates a dataframe object from the given jobname

        e.g.
        dataframe = create_dataframe_from_jobname('Job_12345')

        :param jobname: e.g. 'Job_12345'
        :return: dataframe object
        """
        dataframe_object = self.master_dataframe
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
            dataframe_object = self.master_dataframe
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
        if not dataframe_object:
            dataframe_object = self.master_dataframe
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
    log_dataframe = pd.read_csv(csv_file)
    log_dataframe.index = pd.to_datetime(log_dataframe.pop('date_time'), format='%Y-%m-%d %H:%M:%S.%f')
    #log_dataframe.index = pd.to_datetime(log_dataframe.pop('date_time'), nfer_datetime_format=True)

    #log_dataframe['date_time'] = pd.to_datetime(log_dataframe['date_time'])
    #log_dataframe['date_time'] = pd.date_range('2000-1-1', periods=200, freq='D')
    #log_dataframe = log_dataframe.set_index(['date_time'])
    #print('Issue with source {0}'.format(csv_file))
    return LogDataframe(log_dataframe)



# Utility ****


def file_exists(filename):
    """
    Checks if given file exists

    :param filename: file to check for
    :return: True if file exists, False if not
    """
    return os.path.isfile(filename)


def run_test(**kwargs):
    # TODO Make optional loglevel kwarg work.
    """
    Puts job related udppm log data into a datastructure.

    Optional Params:
    jobname='Job_123456'  <-- Returns structure only related to specific job
    loglevel='INFO'   <-- 'SEVERE', 'ERROR', 'WARN', 'DEBUG', 'INFO'
    :param kwargs: optional params
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
    for item in final_list:
        print(item)
    # Write to Json
    write_log_to_json('logtest.json', final_list)
    # Write to CSV
    populate_log_csv('logtest.csv', final_list)
    # Create Dataframe Object
    return create_dataframe_from_csv('logtest.csv')
