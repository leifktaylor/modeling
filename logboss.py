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


# PART 1: Log Datastructure Creation (List of Dictionaries)

def create_log_datastructure(log_file):
    """
    Return a list of dictionaries.
    Each dictionary contains a time-stamped line from a log entry, split into
    some, or all, of the following keys:
    'date_time' (Always will be in line)
    'log_level' (Always will be in line)
    'job_name'
    'progress'
    'job'
    'status'
    'message' (Always will be in line)

    :param log_file: UDSAgent.log, or udppm.log
    :return: list of dictionaries
    """
    content = read_log_lines_to_list(log_file)
    main_list = read_log_line_list_to_data_structure(content, log_file)
    return main_list


def determine_line_type(line, log_file):
    # Determine if the line type fits a particular template
    # This is the template for udppm job lines:
    if log_file == 'udppm.log':
        return read_jobstatus_line(line)
    # This is the template for UDSAgent lines
    elif log_file == 'UDSAgent.log':
        return read_udsagent_jobstatus_line(line)
    else:
        return None


def read_udsagent_jobstatus_line(line):
    """
    UDSAGENT ONLY
    Reads a udsagent.log line
    :param line: a line from UDSAgent.log
    :return: dictionary of line components
    """
    job_status = {}
    job_status['date_time'] = '{0} {1}'.format(line.split()[0], line.split()[1])
    job_status['log_level'] = line.split()[2]
    # TODO: Account for subjobs.
    # If the type of line where jobname is the 5th element:
    if re.match('Job_\d+', line.split()[4]):
        job_status['job_name'] = re.match('Job_\d+', line.split()[4]).group(0)
        job_status['message'] = ' '.join(line.split()[5:])
    # If the type of line without a jobname...
    else:
        job_status['job_name'] = ''
        job_status['message'] = ' '.join(line.split()[4:])
    job_status['progress'] = ''
    job_status['job'] = ''
    job_status['status'] = ''
    return job_status


def read_jobstatus_line(line):
    """
    UDPPM ONLY
    Reads a udppm.log line and returns a dictionary of line components
    :param line: an input line with the correct format (use 'determine_line_type')
    :return: a dictionary of line components
    """
    # parse a line for jobstatus info and place into dictionary
    item_list = ['job', 'message', 'progress', 'status']
    job_status = {}
    # if it is the type of list where jobname is the 4th element:
    if re.match('Job_\d+', line.split()[3]):
        #TODO: Ad another layer to this parsing.
        #TODO: If it is a jobname 4th element, but there are no blah=
        for item in item_list:
            try:
                job_status[item] = re.search('{0}="(.*?)"'.format(item), line).group(1).strip(':')
            except AttributeError:
                pass
        # add job name
        job_status['job_name'] = line.split()[3].strip(':')
    else:
        job_status['job_name'] = ''
        job_status['progress'] = ''
        job_status['job'] = ''
        job_status['status'] = ''
        job_status['message'] = ' '.join(line.split()[3:])
    # add date information
    job_status['date_time'] = '{0} {1}'.format(line.split()[0], line.split()[1])
    # add log level
    job_status['log_level'] = '{0}'.format(line.split()[2])
    return job_status


def read_log_lines_to_list(log_file):
    # Open file for reading
    with open(log_file, 'r') as file:
        content = file.readlines()
        file.close()
    return content


def read_log_line_list_to_data_structure(line_list, log_file):
    """
    Determines the type of line in the file and properly puts it into the mainlist.
    :param log_file: the type of log. e.g 'UDSAgent.log' or 'uddpm.log'
    :param line_list:
    :return:
    """
    main_list = []
    has_timestamp = ''
    previous_time_stamp = ''
    r = {}
    # Each iteration of this forloop will attempt to add a dictionary to the main_list
    for line in line_list:
        #Determine if line has a time_stamp
        time_stamp = re.match('\d\d\d\d-\d\d-\d\d', line)
        # If a line has a timestamp, use it, and format line
        if re.match('\d\d\d\d-\d\d-\d\d', line):
            r = determine_line_type(line, log_file)
            previous_time_stamp = time_stamp.group(0)
        # If line does not have time_stamp, use the previous time stamp
        else:
            if not previous_time_stamp:
                # If a previous time_stamp doesn't exist
                previous_time_stamp = '2016-01-01 03:03:03'
            # Use the Previous time_stamp
            r['date_time'] = previous_time_stamp
            r['message'] = line
        # Append the line to the line list
        main_list.append(r)
    return main_list

# PART 2: External File Handling
# Log files, after being converted to data structures, are stored in JSON format and CSV Format
# JSON Handling *****


def write_log_to_json(filename, loglist, write_type='w'):
    """
    Populates file with log data in json format.
    :param filename: output file
    :param loglist: list of lines from logfile
    :param write_type: 'w' (overwrite) or 'a' (append)
    :return:
    """
    with open(filename+'.json', 'w') as outputfile:
        json.dump(loglist, outputfile)
        outputfile.close()
    print('Json data written to {0}'.format(filename+'.json'))

# CSV Handling *****


def populate_log_csv(log_type, log_list, write_type='w', overwrite=True, **kwargs):
    # TODO: Improve time stamping in ingest
    """
    Populates CSV from list of log lines.

    :param log_list: list of log lines.
    :param write_type: 'w' (overwrite) or 'a' (append)
    :param log_type: 'udppm.log' or 'UDSAgent.log'
    :return:
    """
    if 'filename' in kwargs:
        log_type = kwargs['filename']
    if overwrite:
        create_csv(log_type+'.csv')
    else:
        # Create a CSV if one doesn't exist
        if not file_exists(log_type+'.csv'):
            create_csv(log_type+'.csv')

    if log_type:
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
        with open(log_type+'.csv', write_type) as log_csv:
            wr = csv.writer(log_csv, quoting=csv.QUOTE_ALL)

            # Write header row
            wr.writerow(['date_time', 'log_level', 'job_name',
                         'status', 'job', 'progress', 'message'])

            # Write log data
            for line in log_lines:
                wr.writerow(line)
        log_csv.close()
    else:
        print('Invalid log type. Accepts "udppm.log" or "UDSAgent.log"')

    print('{0} spreadsheet updated'.format(log_type+'.csv'))
    return log_type+'.csv'


def create_csv(filename):
    """
    Creates a csv file.
    :return: filename
    """
    new_csv = open(filename, 'w')
    new_csv.close()
    return filename

# TODO:
# Matplotlib Graphing

# PART 3: Pandas Dataframe Handling ****


def create_log_dataframe(log_file):
    """
    Returns a dataframe of the given log_file
    :param log_file: 'UDSAgent.log' or 'udppm.log'
    :return: dataframe object
    """
    log_datastructure = create_log_datastructure(log_file)
    print('Total row count of {0} Dataframe is {1}'.format(log_file, len(log_datastructure)))
    csv_file = populate_log_csv(log_file, log_datastructure)
    return create_dataframe_from_csv(csv_file)


class LogDataframe(object):
    def __init__(self, **kwargs):
        """
        Class with a dictionary containing dataframe objects for 'udppm' and 'udsagent' logs.

        Optional Kwaargs:
        printall: Boolean: Prints all queries to screen in addition to returning dataframes.
        df: assign only a single dataframe, do not load all ('udppm', 'udsagent') etc.
        :param kwargs: Optional K-V pairs
        """
        self.df = {}
        if 'df' in kwargs:
            if kwargs['df'] == 'udppm':
                self.df['udppm'] = create_log_dataframe('udppm.log')
            elif kwargs['df'] == 'udsagent':
                self.df['udsagent'] = create_log_dataframe('UDSAgent.log')
        else:
            self.df['udppm'] = create_log_dataframe('udppm.log')
            self.df['udsagent'] = create_log_dataframe('UDSAgent.log')
        if 'printall' in kwargs:
            self.print_all = True

    def show_all(self, **kwargs):
        """
        Shows combined dataframe of all logs. Attempts to match timestamps for side-by-side comparison.
        :param kwargs:
        :return:
        """
        # Truncate logs to show only message and jobname
        udppm = self.df['udppm'][['job_name', 'message']]
        udsagent = self.df['udsagent'][['message']]
        # Change udsagent 'message' column name to avoid duplication error
        # udsagent.columns.values[0] = 'udsmessage'
        # Combine logs into one dataframe
        combined_df = combine_dataframes(udppm, udsagent)
        combined_df.to_csv('combined.csv')

    def select(self, column_name, value, dataframe=''):
        """
        Select from 'column_name' where item == 'value'.

        :param column_name: column name to query
        :param value: value of row in column
        :param dataframe: pandas dataframe object
        :return:
        """
        if not dataframe:
            dataframe = self.df['udppm']
        query = dataframe.ix[dataframe[column_name] == value]
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
        :param df: dataframe to query (udppm or udsagent)
        :param messages: show status messages only (set to True)
        :return: dataframe object
        """
        if 'df' in kwargs:
            dataframe = self.df[kwargs['df']]
        else:
            dataframe = self.df.itervalues().next()
        col_width = 100
        if 'column' in kwargs:
            if 'value' in kwargs and 'has' in kwargs:
                print('CANNOT SHOW DATAFRAME. Choose either "value" or "has", not both.')
            elif 'value' in kwargs:
                print('QUERIED')
                dataframe_object = self.select(kwargs['column'], kwargs['value'], dataframe)
            elif 'has' in kwargs:
                dataframe_object = dataframe[dataframe[kwargs['column']].str.contains(kwargs['has'])]
            else:
                print('Include a "value" or a "has" along with the "column"')
        else:
            dataframe_object = dataframe
        if 't1' and 't2' in kwargs:
            dataframe_object = dataframe_object.ix[kwargs['t1']:kwargs['t2']]
        if 'messages' in kwargs:
            dataframe_object = dataframe_object[['job_name', 'message']]
            col_width = 100
        pd.set_option('display.max_colwidth', col_width)
        pd.set_option('display.max_rows', 1000000)
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
    log_dataframe = pd.read_csv(csv_file, dtype='str')
    log_dataframe.index = pd.to_datetime(log_dataframe.pop('date_time'), format='%Y-%m-%d %H:%M:%S.%f')
    return log_dataframe


def combine_dataframes(dataframe1, dataframe2):
    """
    Combines two dataframes.

    :param dataframe1:
    :param dataframe2:
    :return: concatenated dataframe
    """
                                    #.set_index(['date_time']
    #result = dataframe1.append(dataframe2)
    #result = pd.concat([dataframe1, dataframe2], axis=1)

    #result = dataframe1.join(dataframe2, how='outer')
    result = pd.merge(dataframe1, dataframe2, on='message', how='outer')
    return result
    #return dataframe1.merge(dataframe2)
    #, left_index=True, right_index=True, how='right', lsuffix='_x')


# PART 4: Commandline Use, Utility, File-Handling, Etc
# Utility ****


def file_exists(filename):
    """
    Checks if given file exists

    :param filename: file to check for
    :return: True if file exists, False if not
    """
    return os.path.isfile(filename)

# *** Command Line Functionality (run logboss as executable)


def run_test(**kwargs):
    """
    Puts job related udppm log data into a datastructure.
    jobname='blah' for only a specific job
    :return:
    """
    # TODO: Make df argument allow for 'both' which combines the dataframes
    if 'df' in kwargs:
        if kwargs['df'] == 'udsagent':
            log_file = 'UDSAgent.log'
        if kwargs['df'] == 'udppm':
            log_file = 'udppm.log'
    else:
        log_file = 'udppm.log'
    main_list = create_log_datastructure(log_file)
    final_list = []
    if 'jobname' in kwargs:
        for item in main_list:
            if kwargs['jobname'] == item['job_name']:
                final_list.append(item)
    else:
        final_list = main_list
    # Write to Json
    write_log_to_json(log_file, final_list)
    # Write to CSV
    populate_log_csv(log_file, final_list)
    # Create Dataframe Object
    return LogDataframe(df=log_file)


def parseArguments():
    """
    Parses arguments given at commandline.
    :return:
    """
    parser = argparse.ArgumentParser()
    #Optional Args
    parser.add_argument("-c", "--column", help="select from this column.", default='')
    parser.add_argument("-r", "--row", help="an exact row value.", default='')
    parser.add_argument("-s", "--substring", help="rows that contain this substring", default='')
    parser.add_argument("-m", "--messages", help="status message only", default='')
    parser.add_argument("-df", "--dataframe", help="dataframe to read from 'udppm' or 'udsagent'")
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
    df = args.dataframe
    messages = args.messages
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
    if df:
        kwargs['df'] = df

    # Create Dataframe
    #a = run_test(**kwargs)
    a = LogDataframe(**kwargs)
    a.show(**kwargs)

        # TODO: Plot numerical data of:
        # Length of backup jobs compared to other backup jobs
        # Length of
        # df = a.df.cumsum()
        # plt.figure();
        # df.plot();
