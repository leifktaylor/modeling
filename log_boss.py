import re

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
                job_status[item] = re.search('{0}="(.*?)"'.format(item), line).group(1)
            except AttributeError:
                print('element not found')

    # add date information
    job_status['date_time'] = '{0} {1}'.format(line.split()[0], line.split()[1])
    # add log level
    job_status['log_level'] = '{0}'.format(line.split()[2])
    # add job name
    job_status['job_name'] = line.split()[3]
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


def run_test():
    content = read_log_lines_to_list('udppm.log')
    main_list = read_log_line_list_to_data_structure(content)
    for item in main_list:
        print(item)
