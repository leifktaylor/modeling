from scripts import rmanlog
import re

class RmanLib(rmanlog.RmanLog):
    def __init__(self, filename='', dbname='babydb',
                 ipaddress='172.27.17.125', username='root', password='12!pass345', port=22):
        super(RmanLib, self).__init__(filename=filename, dbname=dbname,
                                      ipaddress=ipaddress, username=username, password=password, port=port)

    def verify_backup_full(self, jobname):
        """
        Verifies that the given job was a level 0 backup (full backup)
        :param jobname: e.g. Job_12345
        :return: True or False
        """
        if self.grep('{0}_Level_0_Backup_Start'.format(jobname)):
            return True
        else:
            return False

    def verify_backup_incremental(self, jobname):
        """
        Verifies that the given job was a level 1 backup (incremental)
        :param jobname: e.g. Job_12345
        :return: True or False
        """
        if not self.grep('{0}_Level_0_Backup_Start'.format(jobname)):
            return True
        else:
            return False

    def list_all_jobs(self):
        """
        Lists all the jobs in the rman log
        :return: list of job names, e.g. ['Job_12345', 'Job_54321']
        """
        linelist = self.grep('Job_')
        joblist = []
        # Parse jobs out of list of lines that contain Job_#####
        for line in linelist:
            joblist.append(re.search('Job_\d+', line).group(0))
        # Convert list to set and back to list to remove duplicate entries
        return list(set(joblist))


