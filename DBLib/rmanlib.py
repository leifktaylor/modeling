from scripts import rmanlog


class RmanLib(rmanlog.RmanLog):
    def __init__(self, filename='', dbname='babydb',
                 ipaddress='172.27.17.125', username='root', password='12!pass345', port=22):
        super(RmanLib, self).__init__(filename=filename, dbname=dbname,
                                      ipaddress=ipaddress, username=username, password=password, port=port)

    def is_job_in_log(self, jobname):
        """
        Verifies that the given job name (e.g. Job_12345) is in the rman log
        :param jobname: e.g. Job_12345
        :return: True or False
        """
        if self.grep(jobname):
            return True
        else:
            return False
