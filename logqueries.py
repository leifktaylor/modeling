from logcheck import *


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
    Verifies that for the given BACKUP job_name:
    SSL Connected
    SSL Handshake done
    #Possible Extra:
    SSL TLS sessions ticket verified

    :param udppm_log_file: udppm log file, e.g. /dumps/udppm.log
    :param job_name: e.g. Job_12345
    :return: True if SSL_connected, or False
    """
    line_list = read_lines_from_log(udppm_log_file, job_name)
    if get_job_type(udppm_log_file, job_name) != 'backup':
        logging.error('Incorrect job type provided. Must be backup job')
        return False
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
    line_list = read_lines_from_log(udppm_log_file, job_name)
    if get_job_type(udppm_log_file, job_name) == 'expire':
        for line in line_list:
            if 'VDisk deletion failed' in line:
                return False
        return True
    else:
        logging.error('Incorrect job type provided, must be expire job')
    return False


def get_job_type(filename, job_name):
    """
    Takes a list of lines that have been filtered for a particular job using 'read_lines_from_log'
    and then returns the job type.

    :param job_name: name of job to search for
    :return: job type
    """
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
    and then returns the job type.

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


def get_error_codes_from_job(log_file, job_name):
    """
    Parses through log and finds error codes that were raised during the job.
    Not guaranteed to find every error, just the ones raised in the log file.

    :param log_file: log file to parse. e.g. udppm.log
    :param job_name: name of job to filter for

    :return: list of error codes
    """
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


def list_jobs_of_type(log_file, job_type):
    """
    Returns a list of all the jobs of given type in the given log file.

    :param log_file: e.g. /dumps/udppm.log
    :param job_type: e.g. 'backup' , 'streamsnap' , 'logreplicate' , 'expire', etc.
    :return: list of jobnames. e.g. ['Job12345', 'Job43763', ...]
    """
    line_list = read_lines_from_log(log_file)
    job_list = []
    for line in line_list:
        if 'job="{0}"'.format(job_type) in line:
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
