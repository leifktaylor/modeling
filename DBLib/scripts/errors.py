# Author: Leif Taylor
# This module handles parsing for Oracle or SQLPlus errors in an output string, and then raising them.

import re


class OracleError(Exception):
    """
    Oracle exception object for (ORA-#####) type errors.
    Oracle errors are sent to stdout and must be caught.
    """
    def __init__(self, errorcode, errormessage):
        self.errormessage = errormessage
        self.errorcode = errorcode
        self.msg = '{0}: {1}'.format(self.errorcode, self.errormessage)

    def __str__(self):
        return self.msg


class SQLPlusError(Exception):
    """
    SQLPlus exception object for (SP2-####) type errors.
    SQLPlus errors are sent to stdout and must be caught.
    """
    def __init__(self, errorcode, errormessage):
        self.errormessage = errormessage
        self.errorcode = errorcode
        self.msg = '{0}: {1}'.format(self.errorcode, self.errormessage)

    def __str__(self):
        return self.msg


class SQLServerError(Exception):
    """
    SQLCmd and SQLServer exception object for 'Msg ###' 'Error message'
    """
    def __init__(self, errorcode, errormessage):
        self.errormessage = errormessage
        self.errorcode = errorcode
        self.msg = '{0}: {1}'.format(self.errorcode, self.errormessage)

    def __str__(self):
        return self.msg


def raise_oracle_error(response):
    """
    Searches stdout for ORA exceptions and raises for error
    """
    output_string = ' '.join(response)
    if re.search('ORA-\d+', output_string):
        # Get error code searching for ORA-#####
        errorcode = re.search('ORA-\d+', output_string).group(0)
        # Extract error message from response (shave off ' :')
        errormessage = output_string.split(errorcode)[1].strip()[2:]
        raise OracleError(errorcode, errormessage)


def raise_sqlplus_error(response):
    """
    Searches stdout for SP2 exceptions and raises for error
    """
    output_string = ' '.join(response)
    if re.search('SP2-\d+', output_string):
        # Get error code searching for ORA-#####
        errorcode = re.search('SP2-\d+', output_string).group(0)
        # Extract error message from response (shave off ' :')
        errormessage = output_string.split(errorcode)[1].strip()[2:]
        raise SQLPlusError(errorcode, errormessage)


def raise_sqlserver_error(response):
    """
    Searches stdout for 'msg' exceptions and raises for error
    """
    # Find error code
    output_string = ' '.join(response)
    error_found = re.search('Msg \d+', output_string)
    if error_found:
        errorcode = error_found.group(0)
        # Find error message in response, will be index after the error code in the stdout line list
        for i in range(0, len(response)):
            if errorcode in response[i]:
                errormessage = response[i+1]
                break
        raise SQLServerError(errorcode, errormessage)
