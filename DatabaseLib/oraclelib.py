# Author: Leif Taylor
# This is a library of sqlplus command that can be executed on a remote host.
# These methods can be used as keywords in Robot Framework.

import oracleconnection


class OracleLib(oracleconnection.OracleConnection):
    """
    Library of keywords which issue sqlplus commands on remote host and handle the output

    Keywords with the prepend 'verify' will raise for error if conditions are not met.
    """
    def __init__(self, ipaddress, username='oracle', password='12!pass345', port=22, sid='', home='', path=''):
        super(OracleLib, self).__init__(ipaddress, username=username, password=password, port=port, sid=sid, home=home, path=path)

    def sqlplus(self, command, *args, **kwargs):
        """
        Issue a mysql command
        Will raise/return Oracle errors

        :param command: e.g 'INSERT INTO mytable VALUES (30, 22, 15)'
        :param args:
        :param kwargs:
        :return: stdout, stderr, rc
        """
        stdout, stderr, rc = self.sqlplus_cmd(command, **kwargs)
        return stdout, stderr, rc

    def query(self, command, *args, **kwargs):
        """
        Query Oracle database and return output as list of dictionaries where:
        list index is database row
        dictionary kv pairs are column/row pairs

        :param command: e.g. 'SELECT * FROM mytable;'
        :param args:
        :param kwargs:
        :return: list of dictionaries
        """
        # Add ';' if not already in command
        if command[-1] != ';':
            command += ';'

        # Add delimiter, line size, and pagesize to command for parsing purposes, and then issue query
        command = 'set colsep "{0}"\nset linesize 32000\nSET PAGESIZE 50000\n'.format(self.delimiter) + command
        stdout, __, __ = self.sqlplus(command)

        # Get Column Names and Find Rows in output
        column_list = []
        table_rows = []
        for i in range(0, len(stdout)):
            if stdout[i]:
                # Get column headers and strip whitespace
                column_list = stdout[i].split(self.delimiter)
                column_list = [item.strip() for item in column_list]
                # Get row values and strip whitespace
                unstripped_rows = [row.split(self.delimiter) for row in stdout[i+2:-1]]
                # Each row is a list, and must have all of the strings within it stripped
                for row in unstripped_rows:
                    # .replace to remove the \t automatically added if there are four spaces in entry
                    table_rows.append([item.strip().replace('\t', '    ') for item in row])
                break

        # Create list of dictionaries where each list index is a row, populated by a dictionary with column/value pairs
        table_data = [dict(zip(column_list, row)) for row in table_rows]
        return table_data

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



# SQL SERVER COMMANDS

    # sqlcmd -q "SQL COMMAND HERE"

    # sqlcmd -q "CREATE DATABASE [SOMENAME]"
                # keep the brackets to the parser doesn't try to interpret
                # command parser interprets anything inside square brackets as a literal
