# Author: Leif Taylor
# This Library maintains an ssh connection with a host running a SQLServer Instance(s)
# Will attempt to connect to default instance if no instance name is provided.

import connection
import errors


class SQLServerConnection(connection.SSHConnection):
    """
    Connect to remote host as oracle user over ssh and issue sqlplus commands while maintaining environmental variables
    """
    def __init__(self, ipaddress, username='Administrator', password='12!pass345', port=22,
                 instance_name='', database=''):
        super(SQLServerConnection, self).__init__(ipaddress, username=username, password=password, port=port)
        # Delimiter used for parsing sqlcmd queries
        self.delimiter = "%"

        # Attempt to find default instance name if instance_name not provided
        if not instance_name:
            self.instance_name = self.find_default_sql_instance()
        else:
            self.instance_name = instance_name

        # If database is supplied, automatically use/create this database for all queries
        if database:
            # If database name is supplied, confirm database exists, create it if it does not
            self.auto_database = False
            self.database = self.init_add_database(database)
            self.auto_database = True
        else:
            self.auto_database = False

    def init_add_database(self, database_name):
        """
        Creates database if does not exist for initializing auto_database
        :return:
        """
        # Check if database already exists and return if it does
        row_list = self.query('select name from sys.databases')
        for row_dict in row_list:
            if row_dict['name'] == database_name:
                return database_name

        # If database does not already exist, create and return name
        self.sqlcmd('create database {0}'.format(database_name))
        return database_name

    def find_default_sql_instance(self):
        """
        Default SQL Instance name is the name of the host.
        :return: host name
        """
        stdout, stderr, rc = self.cmd('hostname')
        instance_name = stdout[0].upper()
        return instance_name

    def sqlcmd(self, command, raise_error=True, **kwargs):
        """
        Issue sqlcmd command on remote host and parse output
        :param command: sql statement
        :param raise_error: raise for error
        :param database: database to query
        :param kwargs:
        :return: stdout, stderr, rc
        """
        # Raise error if no instance specified
        if not self.instance_name:
            raise RuntimeError('No instance provided')

        # TODO:
        # Check if line like 'use <databasename>;' in query, and if it is, don't use auto_database

        # Use Database if auto_database
        if self.auto_database:
            command = 'use {0}; {1}'.format(self.database, command)

        # Create sqlcmd string for parsing and issue command
        final_command = 'sqlcmd -S {0} -W -s "{1}" -Q "{2}"'.format(self.instance_name, self.delimiter, command)

        stdout, stderr, rc = self.cmd(final_command)

        # Check for SQLServer and SQLCmd errors and raise if found
        if raise_error:
            errors.raise_sqlserver_error(stdout)

        return stdout, stderr, rc

    def parse_query(self, output):
        """
        Parse output sqlserver query into a list of dictionaries where each dictionary is a row of kv pairs

        :param output: output of sqlcmd query
        :return: list of dictionaries
        """
        # Find line of stdout that has column headers (it will be the first line where the delimiter appears)
        column_list = []
        delim_present = True
        for i in range(0, len(output)):
            if self.delimiter in output[i]:
                column_list = output[i].split(self.delimiter)
                # Skip over structured '----' and identify index of first row of values
                value_index = i+2
                break
        if not column_list:
            # If column list isn't found:
            # Assume that single column was presented, and therefore delimiter will not be added
            # Find the line containing "----"
            for i in range(0, len(output)):
                if '-' in output[i]:
                    column_list = [output[i-1]]
                    value_index = i+1
                    delim_present = False
                    break
            if not column_list:
                raise RuntimeError('Could not find the header line')

        if delim_present:
            # Skip over the line with the structured '------' and put rows into list, ignoring last two lines of stdout
            row_list = [row.split(self.delimiter) for row in output[value_index:-2]]
        else:
            row_list = [[row] for row in output[value_index:-2]]

        # Zip rows into list dictionaries where [{row_value:column1, row_value:column2}, {row2_value:column1...]
        table_data = [dict(zip(column_list, row)) for row in row_list]
        return table_data

    def query(self, command):
        """
        Run a sqlplus query and parse the output, returning a list of dictionaries
        :return: list of dictionaries where each list element is a dictionary representing a row of data
        """
        # Run sqlcmd query
        stdout, stderr, rc = self.sqlcmd(command)
        return self.parse_query(stdout)











# SQL SERVER COMMANDS

    # sqlcmd -q "SQL COMMAND HERE"

    # sqlcmd -q "CREATE DATABASE [SOMENAME]"
                # keep the brackets to the parser doesn't try to interpret
                # command parser interprets anything inside square brackets as a literal

    # list databases
    # sqlcmd - S <instance name> - Q "select name from sys.databases"

    # query with delimiter and remove trailing whitespace (can only be a single char delim)
    # sqlcmd - S 'AREGWINFSHOST' - Q "use leif1; select * from bigtest" -s "%" -W
