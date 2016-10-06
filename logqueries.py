# from logcheck import *
import re
import logging


def read_lines_from_log(filename, *args, **kwargs):
    """
    Opens a log or any file and returns a list of lines.
    If substring(s) are given as arguments, returns a list only the lines which contain either of the substring(s).

    Default substring filtering logic is: filter='or'
    >> If SubstringA Or SubstringB or SubstringC --> return the line
    If optional param: filter='and'
    >> If SubstringA AND SubstringB both in line --> return the line

    :param filename: file to read from
    :param substring: substring to search for, if left blank, returns all lines.
    :param args: additional substrings to search for
    :param kwargs: kv pairs of arguments. e.g. exclusion=True
    :return: list of lines

    """
    if 'filter' in kwargs:
        filtertype = kwargs['filter']
    else:
        filtertype = 'or'
    final_list = []
    # opens the file and reads lines into a list
    with open(filename, 'r') as log:
        for line in log:
            if args:
                if filtertype == 'or':
                    # if any of the argument substrings in line
                    if any(substring in line for substring in args):
                        final_list.append(line)
                if filtertype == 'and':
                    # if all of the argument substrings in line
                    if all(substring in line for substring in args):
                        final_list.append(line)
            # if no arguments given, just return all lines
            else:
                final_list.append(line)
        log.close()
    return final_list


def verify_substring_in_log(filename, *args, **kwargs):
    """
    NOTE: If multiple substrings are given in args, this will verify that:
    ---Substring_A OR Substring_B OR Substring_C are in log----
    If optional param: filter='or' , then this will verify that:
    ---Substring_A AND Substring_B AND Substring_C are in log

    Returns True if given substring(s) in log,
    Returns False if they are not.
    :param filename: log file, e.g. 'udppm.log', 'UDSAgent.log', etc
    :param args: substrings to check for. e.g. 'failed', or 'Job_12345'
    :return: True or False
    """
    if not args:
        raise ValueError('No substrings given. Cannot parse for anything')
    line_list = read_lines_from_log(filename, *args, **kwargs)
    if not line_list:
        return False
    return True


def confirm_udppm(log_file):
    """
    Confirms that given logfile is a udppm log file, raises error if it isn't.
    :param log_file: udppm log file. e.g. udppm.log
    :return: None
    """
    if 'udppm' not in log_file:
        raise ValueError('Incorrect Log type. Udppm required')


def read_lines_from_list(line_list, *args):
    """
    Similiar to read_lines_from_log.  Reads lines for a list looking
    for particular substrings.  Returns a list of lines containing the
    given substring.

    This function should be used if you are performing iterations on
    log data.  You may initially use read_lines_from_log, and then
    use read_lines_from_list to iterate filters (because this is
    faster)

    :param line_list: list of log lines
    :param args: substrings to search for
    :return: list of lines
    """
    final_list = []
    for line in line_list:
        if args:
            # if any of the argument substrings in line
            for argument in args:
                if argument in line:
                    final_list.append(line)
        # if no arguments given, just return all lines
        else:
            final_list.append(line)
    return final_list


def verify_masked_credentials(filename):
    """
    Verifies that in the given log file, all credentials (passwords) are masked.
    Where format is:
    some_password_related_key#value
    And the value is either masked '****', or blank.
    If a password is not masked, this keyword will return False.

    Example Robot Framework Usage:

    +---------------------------+------------------+
    | verify_masked_credentials | /dumps/udppm.log |
    +---------------------------+------------------+

    |

    :param filename: filename of log file to check in
    :return: True (credentials all masked), or False (unmasked credentials found)
    """
    line_list = read_lines_from_log(filename)
    for line in line_list:
        # split line into base elements
        element_list = ' '.join(line.split('|')).split()
        # iterate through line and find password strings
        val = ''
        for element in element_list:
            if 'password#' in element:
                val = element.split('password#')[1]
                break
            elif 'pass#' in element:
                val = element.split('pass#')[1]
                break
        if val:
            print('found password val: {0}'.format(val))
            # if unmasked value found, return True
            if re.match("^[A-Za-z0-9_-]*$", val):
                print('Possible unmasked credentials found: {0}'.format(element))
                return False
    return True


def verify_ssl_connected(udppm_log_file, job_name):
    """
    Use udppm log file.
    Verifies that for the given BACKUP job_name:
    SSL Connected
    SSL Handshake done
    #Possible Extra:
    SSL TLS sessions ticket verified

    :param udppm_log_file: udppm log file, e.g. /dumps/udppm.log
    :param job_name: e.g. Job_12345
    :return: True if SSL_connected, or False
    """
    confirm_udppm(udppm_log_file)
    line_list = read_lines_from_log(udppm_log_file, job_name)
    if get_job_type(udppm_log_file, job_name) != 'backup':
        raise ValueError('Incorrect job type provided, must be backup job')
    required_checks = 0
    for line in line_list:
        if 'SSL Connected' in line:
            # print(line)
            required_checks += 1
        if 'SSL handshake done' in line:
            # print(line)
            required_checks += 1
    if required_checks >= 2:
        return True
    else:
        return False


def verify_vdisk_deletion_succeeded(udppm_log_file, job_name):
    """
    Verifies that the vdisk deletion for an EXPIRATION job succeeded:
    looks for:
    'errorCode 592... ...VDisk deletion failed'

    :param udppm_log_file: uddpm.log file
    :param job_name: e.g. Job_12345
    :return: True (if job succeeded) or False
    """
    confirm_udppm(udppm_log_file)
    line_list = read_lines_from_log(udppm_log_file, job_name)
    if get_job_type(udppm_log_file, job_name) == 'expire':
        for line in line_list:
            if 'VDisk deletion failed' in line:
                return False
        return True
    else:
        raise ValueError('Incorrect job type provided, must be expire job')
    return False


def get_job_type(filename, job_name):
    """
    Parses udppm.log for the jobtype of the given job name.
    Takes a list of lines that have been filtered for a particular job using 'read_lines_from_log'
    and then returns the job type.

    :param job_name: name of job to search for
    :return: job type
    """
    confirm_udppm(filename)
    line_list = read_lines_from_log(filename, job_name)
    job_type = 'Unknown'
    for line in line_list:
        if 'job=' in line:
            if 'UnknownJobType' not in line:
                job_type = re.search('job="(.*?)"', line).group(1).strip(':')
                return job_type
    return job_type


def get_job_type_from_lines(line_list):
    """
    Takes a list of lines that have been filtered for a particular job using 'read_lines_from_log'
    and then returns the job type from udppm.log.

    :param line_list: list of lines from 'read_lines_from_log' where Job_12345 was the filter.
    :return: job type
    """
    job_type = 'Unknown'
    for line in line_list:
        if 'job=' in line:
            if 'UnknownJobType' not in line:
                job_type = re.search('job="(.*?)"', line).group(1).strip(':')
                return job_type
    return job_type


def get_error_codes_from_job(log_file, job_name, linelist=''):
    """
    Parses through log and finds error codes that were raised during the job.
    Not guaranteed to find every error, just the ones raised in the log file.

    If a linelist is provided instead of a log_file, will search through that.
    If you need to iterate repeatedly, use a linelist.

    :param log_file: log file to parse. e.g. udppm.log
    :param job_name: name of job to filter for
    :param linelist: (optional) for iterations, use a linelist, it is faster.
    :return: list of error codes
    """
    if linelist:
        line_list = read_lines_from_list(linelist, job_name)
    else:
        line_list = read_lines_from_log(log_file, job_name)
    error_list = []
    try:
        for line in line_list:
            if 'errorcode' in line:
                error_list.append(re.search('errorcode \d+', line).group(0).split()[1])
            if 'errorCode' in line:
                error_list.append(re.search('errorCode \d+', line).group(0).split()[1])
    except AttributeError:
        logging.debug('no error codes found')
    return error_list


def get_error_codes_from_all_jobs(log_file):
    """
    Parses udppm.log and returns the error codes for all jobs in the form of a
    dictionary where key is the job_name and value is a list of error codes.

    :param log_file: e.g. udppm.log
    :return: dictionary of lists
    """
    confirm_udppm(log_file)
    error_dict = {}
    line_list = read_lines_from_log(log_file)
    job_list = list_all_jobs(log_file)
    for job in job_list:
        error_list = get_error_codes_from_job(log_file, job, line_list)
        error_dict[job] = error_list
    return error_dict


def list_jobs_of_type(log_file, job_type):
    """
    Returns a list of all the jobs of given type in the given udppm.log file.

    :param log_file: e.g. /dumps/udppm.log
    :param job_type: e.g. 'backup' , 'streamsnap' , 'logreplicate' , 'expire', etc.
    :return: list of jobnames. e.g. ['Job12345', 'Job43763', ...]
    """
    confirm_udppm(log_file)
    line_list = read_lines_from_log(log_file)
    job_list = []
    for line in line_list:
        if 'job="{0}"'.format(job_type) in line:
            job_name = re.search('Job_\d+', line).group(0)
            if job_name not in job_list:
                job_list.append(job_name)
    return job_list


def list_all_jobs(log_file):
    """
    Returns a list of all the jobs in the given udppm.log file.

    :param log_file: e.g. /dumps/udppm.log
    :return: list of jobnames. e.g. ['Job12345', 'Job43763', ...]
    """
    confirm_udppm(log_file)
    line_list = read_lines_from_log(log_file)
    job_list = []
    for line in line_list:
        if 'job=' in line:
            job_name = re.search('Job_\d+', line).group(0)
            if job_name not in job_list:
                job_list.append(job_name)
    return job_list


def verify_hello_connector():
    """
    verifies that hello connector messages was sent by udppm on the sky/cds,
    and received by udsagent on the host.
    :return:
    """
    # TODO: Finish
    pass


def verify_restore_job_succeeded(udppm_log_file, job_name):
    """
    Checks udppm.log to confirm that restore job has succeeded.

    :return: True or False
    """
    confirm_udppm(udppm_log_file)
    if get_job_type(udppm_log_file, job_name) == 'restore':
        for line in line_list:
            if 'Restore job completed successfully' in line:
                return True
        return False
    else:
        logging.error('Incorrect job type provided, must be restore job')
    return False


def verify_backup_inband(logfile, job_name):
    """
    Use this KW on a udppm.log file.
    Verifies that given snapshot job was inband.
    (At least that the log said it was inband)

    :param logfile: logfile, e.g. 'udppm.log'
    :param job_name: e.g. Job_12345
    :return:
    """
    confirm_udppm(logfile)
    if get_job_type(logfile, job_name) != 'backup':
        raise ValueError('Incorrect job type provided, must be backup job')
    # check if the job is even found in the log
    if verify_substring_in_log(job_name):
        if verify_substring_in_log('Prepared snapshot for inband', job_name, filter='and'):
            return True
        else:
            return False
    else:
        raise ValueError('Job not found in given log file')

