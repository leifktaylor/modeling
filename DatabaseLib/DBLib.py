# Author: Leif Taylor / November 2016
# This library is designed for use in Robot Framework.  It allows you to use the same keywords interchangeably for
# SQLServer and Oracle Databases.  Run queries, confirm row counts, make and drop tables, all with the same
# exact keywords.

import oraclelib
import sqlserverlib


class DatabaseLib(object):
    def __init__(self, ipaddress, username, password, type, port=22, db='', instance_name='', home='', path=''):
        """
        When using this class, make sure you give the 'type' parameter correctly, 'Oracle', or 'SQL'

        ORACLE:
        If you select 'Oracle' as the type, you must provide a 'db' parameter where db is the oracle_SID

        SQL:
        If you select 'SQL', the 'db' parameter will point to a database, and is not required but recommended
                    as the 'auto_database' feature will create the given database if it doesn't exist, and
                    automatically prepend 'use <databasename>;' to all commands.

                    instance_name is for SQL only, and is not required as the default instance will
                    automatically be detected.  If you are using an instance other than the default,
                    provide the 'instance_name'.

        :param ipaddress: of host
        :param username: oracle user, ssh_user for sqlserver
        :param password: oracle_pass or ssh_user pass for sqlserver
        :param type: important: 'Oracle' or 'SQL'
        :param port: port used for ssh
        :param db: (required) if type='Oracle' this is the Oracle_SID, (optional) if SQL, this is a database
        :param instance_name: if type='SQL' manually specify instance name, otherwise default is detected
        :param home: (optional) Oracle only: automatically determined if not provided
        :param path: (optional) Oracle only: automatically determined if not provided
        """
        # if type.upper() = 'ORACLE':
        #     super(OracleLib, self).__init__(ipaddress, username=username, password=password, port=port, sid=db,
        #                                     home=home, path=path)
        # elif type.upper() = 'SQL':
        #     super(SQLServerLib, self).__init__(ipaddress, username=username, password=password,
        #                                        port=port, database=db, instance_name=instance_name)
        # else:
        #     raise RuntimeError("Unknown database type provided. Use 'SQL' or 'Oracle'")
        # if type == 'ORACLE'
        #     self.database = OracleLib()
        #
        # DatabaseLib.verify_row_count()
        #
        # try:
        #     self.verify_row_count()
        # except MethodDoesntExist