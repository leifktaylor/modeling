import paramiko


class OracleError(Exception):
    """
    Oracle exception object with error codes.
    """
    errorcodes = [('ORA-00942', 'table or view does not exist'),
                  ('ORA-00923', 'FROM keyword not found where expected'),
                  ('ORA-00922', 'missing or invalid option'),
                  ('ORA-00936', 'missing expression'),
                  ('ORA-00904', 'invalid identifier'),
                  ('ORA-00955', 'name is already used by an existing object'),
                  ('ORA-00907', 'missing right parenthesis'),
                  ('ORA-01722', 'invalid number'),
                  ('ORA-00902', 'invalid datatype')]


class SQLPlusError(Exception):
    """
    SQLPlus exception object (SP2-####) with error codes.
    """
    errorcodes = [('SP2-0042:', 'unknown command - rest of line ignored.'),
                  ('SP2-0734:', 'unknown command - rest of line ignored.'),
                  ('SP2-0223:', 'No lines in SQL buffer.'),
                  ('SP2-0172:', 'No HELP matching this topic was found.')]


class SSHConnection(object):
    """
    This class connects to a host when initialized.
    SSHConnection can issue shell commands and receive output
    """
    def __init__(self, ipaddress, username='root', password='12!pass345', port=22, **update_cmds):
        # Connection params
        self.ipaddress = ipaddress
        self.username = username
        self.password = password
        self.port = port

        # Dictionary of update commands
        self.connection_params = update_cmds

        # Connect
        self.client = self.connect()

    def connect(self):
        """
        Connect to remote host
        :return: paramiko SSHClient object
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.ipaddress, username=self.username, password=self.password, port=self.port, **self.connection_params)
        return client

    def raw_cmd(self, command, ascii=False):
        """
        Issue direct command over ssh
        :param command: command to issue
        :param ascii: Attempt to convert to ascii if true, if false return unicode
        :return: stdout (list of lines), stderr (list of lines), return code (integer)
        """
        stdin, stdout, stderr = self.client.exec_command(command)
        stdin.close
        rc = stdout.channel.recv_exit_status()
        if ascii:
            stdout_final = [line for line in stdout.read().splitlines()]
            stderr_final = [line for line in stderr.read().splitlines()]
        else:
            stdout_final = stdout.readlines()
            stderr_final = stderr.readlines()
        return stdout_final, stderr_final, rc

    def cmd(self, command, ascii=True, raise_error=True):
        """
        Issue direct command over ssh, with handlers, can raise for error and attempt to convert to ascii
        :param command:
        :param ascii:
        :param raise_error:
        :return: stdout (list of lines), stderr (list of lines), return code (integer)
        """
        stdout, stderr, rc = self.raw_cmd(command, ascii=ascii)
        if raise_error:
            if rc != 0:
                # If ascii set to false, error message will have u'<message>\n'
                raise RuntimeError(str(stderr) + 'with rc: ' + str(rc))
        return stdout, stderr, rc


class OracleEnv(object):
    """
    Structure which holds environmental variables for active ssh connection
    """
    def __init__(self, oracle_sid, oracle_home, oracle_path):
        if not oracle_sid or not oracle_home or not oracle_path:
            raise RuntimeError('Must provide sid, home, and path')
        self.sid = oracle_sid
        self.home = oracle_home
        self.path = oracle_path


class OracleConnection(SSHConnection):
    """
    Connect to remote host as oracle user over ssh and issue sqlplus commands while maintaining environmental variables
    """
    def __init__(self, ipaddress, username='oracle', password='12!pass345', port=22, sid='', home='', path=''):
        super(OracleConnection, self).__init__(ipaddress, username=username, password=password, port=port)

        # Attempt to find Oracle environmental variables using SID if not provided
        if sid and not home and not path:
            home, path = self.determine_oracle_environmental_variables(sid)

        # Instantiate OracleEnv class which holds oracle environmental variables
        self.oracle_env = OracleEnv(sid, home, path)

    def determine_oracle_environmental_variables(self, sid):
        """
        Attempts to find oracle home and oracle path directories using SID to search for init<sid>.ora
        :param sid: ORACLE_SID e.g. mydb1
        :return: oracle_home, oracle_path
        """
        # Find Oracle_Home directory by searching for database init or spfile
        stdout, stderr, rc = self.cmd("find / -type f -name 'init{0}.ora' 2>/dev/null".format(sid), raise_error=False)
        if not stdout:
            # If init.ora not found, search for spfile
            stdout, stderr, rc = self.cmd("find / -type f -name 'spfile{0}.ora' 2>/dev/null".format(sid), raise_error=False)
            if not stdout:
                # If neither spfile nor init.ora found, raise error
                raise RuntimeError('Could not automatically determine oracle env, please provide SID, home and path')
            orahome = stdout[0].rstrip('dbs/spfile{0}.ora'.format(sid))
        else:
            orahome = stdout[0].rstrip('dbs/init{0}.ora'.format(sid))

        # Set oracle_path to orahome/bin
        orapath = '{0}/bin'.format(orahome)

        return orahome, orapath

    def sqlplus_cmd(self, command, ignore_env=False, **kwargs):
        """
        Export Oracle_Home, SID, and Path, open sqlplus session as sysdba, and issue 'command'
        :param command: sql statement
        :param ignore_env: default False, if True will attempt to launch sqlplus if no environmental variables are given
        :param kwargs:
        :return:
        """
        # Raise error if oracle env not initialized and ignore_env is set to False
        if not ignore_env and not self.oracle_env:
            raise RuntimeError('No oracle environment, use init_oracle_env')

        # Create string which exports environmental variables from OracleEnv class (self.oracle_env)
        oracle_exports = 'export PATH={0}:$PATH;' \
                         'export ORACLE_HOME={1};' \
                         'export ORACLE_SID={2}'.format(self.oracle_env.path, self.oracle_env.home,
                                                        self.oracle_env.sid)

        # Issue concatinated one line command which exports variables, opens sqlplus, and issues a sqlplus statement
        final_command = oracle_exports + ';' + 'echo "' + command + '" | sqlplus -S / as sysdba'
        stdout, stderr, rc = self.cmd(final_command)

        # Check for ORA error messages and return
        self.raise_oracle_error(stdout)
        return stdout, stderr, rc

    @staticmethod
    def raise_oracle_error(response):
        """
        Searches stdout for ORA exceptions and raises for error
        """
        output_string = ' '.join(response)
        for tuple in OracleError.errorcodes:
            if tuple[0] in output_string:
                raise OracleError(tuple[1])

    @staticmethod
    def raise_sqlplus_error(response):
        """
        Searches stdout for SP2 exceptions and raises for error
        """
        output_string = ' '.join(response)
        for tuple in SQLPlusError.errorcodes:
            if tuple[0] in output_string:
                raise SQLPlusError(tuple[1])


class DatabaseLib(OracleConnection):
    """
    Library of keywords which issue sqlplus commands on remote host and handle the output

    Keywords with the prepend 'verify' will raise for error if conditions are not met.
    """
    def __init__(self, ipaddress, username='oracle', password='12!pass345', port=22, sid='', home='', path=''):
        super(DatabaseLib, self).__init__(ipaddress, username=username, password=password, port=port, sid=sid, home=home, path=path)

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
        #self.raise_for_error(stdout)
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

        # Set line size for parsing, and issue query
        command = 'set linesize 32000\nSET PAGESIZE 50000\n' + command
        stdout, __, __ = self.sqlplus(command)

        # Get Column Names and Find Rows in output
        column_list = ''
        for i in range(0, len(stdout)):
            if stdout[i]:
                column_list = stdout[i].split()
                table_rows = [row.split() for row in stdout[i+2:-1]]
                break

        # Create list of dictionaries where each list index is a row, populated by a dictionary with column/value pairs
        table_data = []
        for row in table_rows:
            table_data.append(dict(zip(column_list, row)))
        return table_data

    def verify_database_open(self):
        """
        Verifies database is open for read and write
        :return: True / False
        """
        r = self.sqlplus('select open_mode from v\$database;')
        if 'OPEN_MODE' in r[0] and 'READ WRITE' in r[0]:
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
        stdout, __, __ = self.sqlplus('select count(*) from {0}'.format(tablename))
        for line in stdout:
            if rows in line:
                return True
            else:
                return False



# SQL SERVER COMMANDS

    # sqlcmd -q "SQL COMMAND HERE"

    # sqlcmd -q "CREATE DATABASE [SOMENAME]"
                # keep the brackets to the parser doesn't try to interpret
                # command parser interprets anything inside square brackets as a literal
