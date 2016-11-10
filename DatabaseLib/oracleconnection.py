# Author: Leif Taylor
# This Library maintains an ssh connection with a host running an Oracle Database.
# It allows maintaining of environmental variables (oracle_sid, oracle_home), and executes and parses sqlplus commands.

import errors
import connection


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


class OracleConnection(connection.SSHConnection):
    """
    Connect to remote host as oracle user over ssh and issue sqlplus commands while maintaining environmental variables
    """
    def __init__(self, ipaddress, username='oracle', password='12!pass345', port=22, sid='', home='', path=''):
        super(OracleConnection, self).__init__(ipaddress, username=username, password=password, port=port)
        # Delimiter used for parsing sqlplus queries
        self.delimiter = "MiLeD"

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
            orahome = stdout[0].replace('/dbs/spfile{0}.ora'.format(sid), '')
        else:
            orahome = stdout[0].replace('/dbs/init{0}.ora'.format(sid), '')

        # Set oracle_path to orahome/bin
        orapath = '{0}/bin'.format(orahome)

        return orahome, orapath

    def sqlplus_cmd(self, command, ignore_env=False, raise_error=True, **kwargs):
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

        # Check for ORA or SP2 error messages and return
        if raise_error:
            errors.raise_oracle_error(stdout)
            errors.raise_sqlplus_error(stdout)
        return stdout, stderr, rc
