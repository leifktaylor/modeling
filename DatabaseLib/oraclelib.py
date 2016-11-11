# Author: Leif Taylor
# This is a library of sqlplus command that can be executed on a remote host.
# These methods can be used as keywords in Robot Framework.

from models import oracleconnection
from models.errors import *


class OracleLib(oracleconnection.OracleConnection):
    """
    Library of keywords which issue sqlplus commands on remote host and handle the output

    To construct keywords, use:
    For issuing insert/delete/create/etc:   stdout, stderr, rc = self.sqlplus('your command here')
    For queries (select, show):             row_list = self.query('your select statement here')

    Keywords with the prepend 'verify' will raise for error if conditions are not met.
    """
    def __init__(self, ipaddress, username='oracle', password='12!pass345', port=22, sid='', home='', path=''):
        super(OracleLib, self).__init__(ipaddress, username=username, password=password, port=port, sid=sid, home=home, path=path)

    def verify_database_open(self):
        """
        Verifies database is open for read and write
        :return: True / False
        """
        r = self.query('select open_mode from v\$database;')
        if r[0]['OPEN_MODE'] == 'READ WRITE':
            return True
        else:
            return False

    def verify_archivelog_mode(self):
        """
        Verifies that archivelog mode is enabled
        :return: True / False
        """
        r = self.query('select log_mode from v\$database;')
        if r[0]['LOG_MODE'] == 'ARCHIVELOG':
            return True
        else:
            return False

    def verify_pmon_running(self):
        """
        Verifies pmon is running
        :return: True / False
        """
        stdout, __, __ = self.cmd('ps -ef | grep pmon')
        for item in stdout:
            if self.oracle_env.sid in item:
                return True
        return False

    def verify_row_count(self, tablename, rows):
        """
        Verifies that the given table has the correct amount of rows
        :param tablename: name of table in database
        :param rows: amount of rows expected in table
        :return: True / False
        """
        r = self.query('select count(*) from {0};'.format(tablename))
        if r[0]['COUNT(*)'] == str(rows):
            return True
        else:
            return False

    def verify_table_exists(self, tablename):
        """
        Verifies given table exists
        :param tablename: name of table to check for
        :return: True / False
        """
        try:
            self.query('select * from {0};'.format(tablename))
        except OracleError as e:
            if e.errorcode == 'ORA-00942':
                return False
            else:
                raise OracleError
        return True
