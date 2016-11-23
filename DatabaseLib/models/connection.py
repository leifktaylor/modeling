# Author: Leif Taylor
# This module is used for creating sshconnections to remote hosts, issuing commands, and receiving output.

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
