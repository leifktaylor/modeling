import connection


class RmanLog(object):
    """
    Rman Log class holds rman log attributes including:
    self.filename  - filename of rman log, e.g.
    self.lines()   - list containing all the lines of the rman log file.
    """
    def __init__(self, filename='', dbname='babydb',
                 ipaddress='172.27.17.125', username='root', password='12!pass345', port=22):
        self.dbname = dbname
        self.a = connection.SSHConnection(ipaddress=ipaddress, username=username, password=password, port=port)
        if filename:
            self.filename = filename
        elif dbname:
            self.filename = '{0}_rman.log'.format(dbname)
        else:
            raise RuntimeError('No filename or dbname given. No Rman log to open')

    def log(self):
        """
        Returns list of all the lines in rman log
        :return: list
        """
        sftp_client = self.a.client.open_sftp()
        remote_file = sftp_client.open('/var/act/log/{0}'.format(self.filename))
        line_list = []
        try:
            for line in remote_file:
                line_list.append(line.rstrip('\n'))
        finally:
            remote_file.close()
        return line_list

    def grep(self, substring, i=False):
        """
        Returns the lines which contain the given substring in the log
        :param substring: any substring e.g. 'Job_12345'
        :param i: like grep -i (case insensitive)
        :return: list of lines
        """
        if i:
            return [s for s in self.log() if substring.lower() in s.lower()]
        else:
            return [s for s in self.log() if substring in s]
