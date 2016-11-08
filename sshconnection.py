import paramiko


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
        :return: stdout, stderr, return code
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
        :return:
        """
        stdout, stderr, rc = self.raw_cmd(command, ascii=ascii)
        if raise_error:
            if rc != 0:
                # If ascii set to false, error message will have u'<message>\n'
                raise RuntimeError(stderr)
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
        self.oracle_env = OracleEnv(sid, home, path)

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
        final_command = oracle_exports + ';' + 'echo "' + command + '" | sqlplus / as sysdba'
        return self.cmd(final_command)


class OracleLib(OracleConnection):
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
