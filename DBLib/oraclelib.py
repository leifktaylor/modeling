# Author: Leif Taylor
# This is a library of sqlplus commands that can be executed on a remote host.
# These methods can be used as keywords in Robot Framework.

from scripts import oracleconnection
from scripts.errors import *


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

    def check_oracle_sid(self):
        """
        This keyword is for debugging, to confirm oraclelib has the correct oracle_sid.
        Will return the current oracle_sid that is selected.  To change oracle_sid, use 'change_database()'
        :return: oracle_sid in self.oracle_env
        """
        return self.oracle_env.sid

    def change_database(self, new_sid, auto_correct=True):
        """
        Changes the SID of the oracle_env object in OracleLib.
        All keywords will now act on the database_sid that you have changed to.

        Note:
        Because mounted child instances can have numbers appended to them, auto_correct
        will attempt to find the new child sid even if you have forgotten to add an append.
        e.g. if you enter 'achild' as your sid, but the actual database sid is 'achild1'

        :param new_sid: oracle_sid to change to
        :param auto_correct: automatically determine sid name, e.g. 'achild' is actually 'achild1'
        :return: actual new oracle_sid of running instance
        """
        stdout, stderr, rc = self.cmd('ps -ef | grep pmon | grep {0} | grep -v grep'.format(new_sid))
        if not stdout:
            raise RuntimeError('No SID found, is instance running?')
        # Search ps output for running oracle instance with new_sid name
        if auto_correct:
            for line in stdout:
                if new_sid in line:
                    actual_sid = line.split('ora_pmon_')[-1]
                    self.oracle_env.sid = actual_sid
                    return actual_sid
        else:
            self.oracle_env.sid = new_sid
        # If new oracle_sid not found, or instance not running
        raise RuntimeError('Oracle_SID: {0} not found, or instance not running'.format(new_sid))

    def db_verifications(self):
        """
        Set of standard verifications to make sure Oracle Database is online, mounted, open, archivemode, and running.
        :return: True / False
        """
        if not self.verify_database_open():
            raise RuntimeError('Database not open for read write')
        if not self.verify_archivelog_mode():
            raise RuntimeError('Database not in archivelog mode')
        if not self.verify_pmon_running():
            raise RuntimeError('Pmon is not running. DB Instance down')

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

    def create_table_set_rows(self, tablename, rowcount):
        """
        This method should be used for db/log backup verification to set rows in a table for
        later verifications.

        If the table does not exist, it is created, and the rows are set.
        If the table exists already, it is dropped, created again and the rows are set

        :param tablename: table to create
        :param rowcount: number of rows to set
        :return: datetime on host
        """
        # Delete table if exists
        try:
            self.sqlplus('drop table {0};'.format(tablename))
        except OracleError as e:
            if e.errorcode != 'ORA-00942':
                raise OracleError

        # Create generic table
        self.sqlplus('create table {0} (firstname varchar(30), lastname varchar(30));'.format(tablename))
        # Add rows
        for i in range(0, int(rowcount)):
            self.sqlplus("insert into {0} values ('name{1}', 'lastname{1}');".format(tablename, i))
        # Verify rows correctly added
        self.verify_row_count(tablename, int(rowcount))

        # Return the time
        return self.get_time()

    ###### Diskgroup related commands

