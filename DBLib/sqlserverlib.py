# Author: Leif Taylor
# This is a library of sqlplus command that can be executed on a remote host.
# These methods can be used as keywords in Robot Framework.

from scripts import sqlserverconnection
from scripts.errors import *


class SQLServerLib(sqlserverconnection.SQLServerConnection):
    """
    Library of keywords which issue sqlcmd commands on remote host and handle the output

    Note: When passing in 'database' argument on instantiation 'use <db_name>;' will be prepended to all queries
    and commands.

    To construct keywords, use:
    For issuing insert/delete/create/etc:   stdout, stderr, rc = self.sqlcmd('your command here')
    For queries (select, show):             row_list = self.query('your select statement here')

    Keywords with the prepend 'verify' will raise for error if conditions are not met.
    """
    def __init__(self, ipaddress, username='Administrator', password='12!pass345', port=22, database='', instance_name=''):
        super(SQLServerLib, self).__init__(ipaddress, username=username, password=password,
                                           port=port, database=database, instance_name=instance_name)

    def change_database(self, name, create=False):
        """
        Change the database which SQLServerLib automatically queries.
        :param name: name of database to change to
        :param create: if database doesn't exist, create it.
        """
        # Get list of all databases in instance
        db_list = self.list_databases()
        # Return error if DB doesn't exist
        if name in db_list:
            self.database = name
        else:
            if create:
                self.sqlcmd('create database {0}'.format(name))
            else:
                raise RuntimeError('Database {0} does not exist'.format(name))

    def verify_row_count(self, tablename, rows):
        """
        Verifies that the given table has the correct amount of rows
        :param tablename: name of table in database
        :param rows: amount of rows expected in table
        :return: True / False
        """
        r = self.query('select count(*) from {0};'.format(tablename))
        if r[0][' '] == str(rows):
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
        except SQLServerError as e:
            if e.errorcode == 'Msg 208':
                return False
            else:
                raise
        return True

    def list_databases(self):
        """
        Lists all databases in sqlserver instance
        :return: list of database names
        """
        r = self.query('select name from sys.databases;')
        db_list = list(set().union(*(d.values() for d in r)))
        return db_list

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
            self.sqlcmd('drop table {0};'.format(tablename))
        except SQLServerError as e:
            if e.errorcode != 'Msg 3701':
                raise SQLServerError

        # Create generic table
        self.sqlcmd('create table {0} (firstname varchar(30), lastname varchar(30));'.format(tablename))
        # Add rows
        for i in range(0, int(rowcount)):
            self.sqlcmd("insert into {0} values ('name{1}', 'lastname{1}');".format(tablename, i))
        # Verify rows correctly added
        self.verify_row_count(tablename, int(rowcount))

        # Return the time
        return self.get_time()
