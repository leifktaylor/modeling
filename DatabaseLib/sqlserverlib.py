# Author: Leif Taylor
# This is a library of sqlplus command that can be executed on a remote host.
# These methods can be used as keywords in Robot Framework.

from models import sqlserverconnection


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
