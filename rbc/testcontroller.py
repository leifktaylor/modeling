import os
import sys
import re
import fnmatch
import re
import paramiko
import pprint
from subprocess import call
import tempfile

# ** testcontroller.py **
# maintainer: Leif Taylor
# Purpose: This program will execute a series of robot tests, move the logs into a folder structure, and
# route console input into an output file.
#
# +--------------------------+
# | How to use this program: |
# +--------------------------+
# 1) You must already have your own folder, with inventory files, on a robot controller vm
# 2) Required files: 'rbc', 'aliases', 'testcontroller.py (this file)'
# 3) Edit your 'aliases' file (must be called aliases) like this:
#   [<alias name>]
#   <some command>
#   [<another alias>]
#   <another command>
#   [<another alias>]
#   [another command]
#
# Here is an example aliases file (comments are okay on the tag line, not the invdrobot command line:
#   [aix] # this will run the database test on my aix inventory file
#   oraclehost.py:host mycds.py suites/orarac1+2/databasetest.robot
#   [linux] # this will run the database test on my linux inventory file and a sky
#   linuxoracle.py:host mysky.py suites/orarac1+2/databasetest.robot
#   [dartest]
#   cds1.py:local cds2.py:remote linuxhost1.py:host1 linuxhost2.py:host2 suites/app2host/dartest.robot
#
# 4) To execute all of the tests in the 'aliases' file, simply run: './rbc -a'
# 5) To execute a single test from the 'aliases' file, simply run: './rbc <aliasname>' (e.g. ./rbc aix)
# 6) If you want to execute some but not all, simply list the ones you want: './rbc alias1 alias3 alias5
# 7) For additional help and examples, use './rbc'
#
# Happy Testing!

# TODO: Each test run should have its own console.out, put with the logs, instead of a single one.
local_image = True

class AliasReader(object):
    """
    Parses aliases file and puts contents into dictionary like:
    {'<alias name': '<command>', '<another_alias>': '<another command>', etc}
    """
    def __init__(self, alias_file='aliases', smartread=True, debug=False):
        """
        Parse through 'aliases' file

        With smartread enabled, 'aliases' file should be populated thusly:

        [aliasname]
        inventoryfile.py anotherinventory.py somehost.py:host path/to/test.robot
        [anotheralias]
        ....

        :param alias_file: file called 'aliases' contains the params to execute robot tests
        :param smartread: Allows for truncated verbose alias commands
        """
        # Check that aliases file exists, if it doesn't, create a template:
        if not os.path.isfile(alias_file):
            print('No alias file was found, create a file called aliases in this folder like:')
            print('[some_alias_name]')
            print('<some command with invdrobot or robot>')
            print('[another_alias]')
            print('<some other invdrobot command>')
            with open(alias_file, "a") as af:
                af.write('[mysystem] # This is a template inventory file\n')
                af.write('myappliance.py mysqlhost1.py:source mysqlhost2.py:target /suites/sql/sqlworkflows.robot:\n')
                af.write('[anothersystem]\n')
                af.write('myappliance.py rac1.py:host /suits/orarac1+2/oracle_test.robot\n')
                af.close()
            raise RuntimeError('No alias file found, created an alias file called aliases, with example')

        # Parse out aliases file and create a dictionary of aliases and commands
        self.smartread = smartread

        if debug:
            print('In debug mode, will not load alias file automatically')
        else:
            self.alias_file = alias_file
            self.aliases = self.dict_aliases(self.list_lines())

    def list_lines(self):
        """
        :return: List of lines from aliases file
        """
        # Open aliases file and read lines
        with open(self.alias_file) as source_file:
            line_list = [line.rstrip('\n') for line in source_file]
            source_file.close()
        return line_list

    def dict_aliases(self, line_list):
        """
        Returns a dictionary of aliases and their commands
        :param line_list: list of lines from self.aliases file
        :return: {<aliasname>: <invdrobot command>}
        """
        # Parse and place lines into dictionary
        alias_dict = {}
        for i in range(0, len(line_list)):
            match = re.search(r"\[([A-Za-z0-9_]+)\]", line_list[i])
            if match:
                alias_dict[match.group(1)] = line_list[i+1]
        if self.smartread:
            return self._smartread(alias_dict)
        else:
            return alias_dict

    def _smartread(self, alias_dict):
        """
        Converts a dictionary of truncated alias commands into full robot commands
        :param alias_dict: dictionary generated from dict_aliases
        :return: dictionary
        """
        for alias, command in alias_dict.items():
            long_command = self.generate_robot_command(command)
            alias_dict[alias] = long_command
        return alias_dict

    def generate_robot_command(self, alias_command):
        """
        Takes an alias from aliases file and translates into a docker robot command:
        Will turn:
        alfalfa.py NSTLPAR18_nathan.py:rac1 NSTLPAR18_nathan.py:rac2 suites/orarac1+2/logsmart_appaware_local.robot
        Into:
        docker run --rm -v "/ragu":/home/testing/robot/inv brianwilliams/framework3 robot -d inv/ -L DEBUG:INFO "$@" -V inv/appliance/alfalfa.py -V inv/host/NSTLPAR18_nathan.py:rac1 -V inv/host/NSTLPAR18_nathan.py:rac2 suites/orarac1+2/logsmart_appaware_local.robot
        :param args:
        :return:
        """
        # First create the base command string:
        if local_image:
            base_string = 'docker run -ti -v /Users/actifioadmin/PycharmProjects/framework3:/home/testing ' \
                          'brianwilliams/framework3 robot --loglevel DEBUG:INFO'
        else:
            base_string = 'docker run --rm -v "{0}":/home/testing/robot/inv brianwilliams/framework3 ' \
                          'robot -d inv/ -L DEBUG:INFO "$@"'.format(os.path.abspath('.'))

        # Cut out any comments (once # has appeared, remove it and everything after), isolate inventory names
        uncommented_line = alias_command.split('#')[0].rstrip()
        alias_words = uncommented_line.split()

        # Find the reference to the .robot test
        robotfile = self._find_robot_file_reference_in_command(alias_words)
        alias_words.remove(robotfile)

        # Find the full paths to all of the inventory files, and convert into -V command
        full_paths = ['-V {0}'.format(self.get_full_name_with_prepend(filename)) for filename in alias_words]

        # Return fully concatenated command
        full_paths_string = ' '.join(full_paths)
        return '{0} {1} {2}'.format(base_string, full_paths_string, robotfile)

    def _find_robot_file_reference_in_command(self, word_list):
        """
        Finds a reference to a .robot file in a string of words
        :param word_list: some command string that references a robot file
        :return: the robot filename
        """
        robotfile = ''
        for item in word_list:
            if '.robot' in item:
                return item
        if not robotfile:
            raise RuntimeError('Could not find reference to a .robot file in your alias: {0}\n '
                               'Run this program with the "tests" flag for .robot test list'.format(alias_command))

    def get_full_name_with_prepend(self, name):
        """
        Takes inventory file name, and finds the full path.  If a robot test prepend is on the filename,
        will take that into account and append it back onto the full path.
        e.g. mycds.py:Local becomes inv/appliance/mycds.py:Local
        :return: full path with 'prepend' if present
        """
        if ':' in name:
            prepend = name.split(':')[1]
            filename = name.split(':')[0]
            return self.find_inventory_file(filename) + ':' + prepend
        else:
            return self.find_inventory_file(name)

    def find_inventory_file(self, name):
        """
        Returns full path of inventory file
        :return:
        """
        for root, dirs, files in os.walk('.'):
            if name in files:
                pathname = os.path.join(root, name)
                return 'inv{0}'.format(pathname[1:])
        raise RuntimeError('Could not find the inventory file "{0}"'.format(name))

    def print_aliases(self):
        """
        Prints aliases with alias name, and command
        :return:
        """
        for alias, command in self.aliases.items():
            print "'{0}' : '{1}'".format(alias, command)


class TestController(object):
    """
    Execute commands from aliases file and move log files to nested folders
    """
    def __init__(self, outputfile='console.out', output_append=True):
        """
        :param outputfile: file where console output from tests will go
        :param output_append: automatically output all test console output to outputfile
        """
        self.aliases = AliasReader().aliases
        self.outputfile = outputfile
        # Append redirection to output file to all alias commands
        if output_append:
            for alias, command in self.aliases.items():
                self.aliases[alias] = '{0} >> {1} 2>&1'.format(command, self.outputfile)

    def run_test(self, alias):
        # Echo commencing line into outputfile
        start_date = self.date()
        self.echo_out('**** STARTING TEST: {0} at {1} ****'.format(alias, self.full_date()))

        # Execute test after checking if .robot file exists
        invdrobot_command = self.aliases[alias]
        robot_file = invdrobot_command.split()
        self.cmd(invdrobot_command)

        # Echo ending line into outputfile
        self.echo_out('**** TEST COMPLETED ****')

        # Move logs, html and xml files to logs folder like 'logs/<date>/<alias>'
        self.move_files(alias, start_date)
        self.echo_out('**** Logs moved to logs/{0}/{1}'.format(start_date, alias))

    def run_tests(self):
        for alias, command in self.aliases.items():
            self.run_test(alias)

    def make_log_directory(self, alias, date):
        command = 'mkdir -p logs/{0}/{1}'.format(date, alias)
        self.cmd(command)

    def move_files(self, alias, date):
        files = ['log.html', 'output.xml', 'report.html']
        # Check that files actually exist
        for f in files:
            if not os.path.isfile(f):
                raise RuntimeError('{0} not found! Did a robot test execute and save files?'.format(f))

        # Create target directory based off of alias name and date
        target_directory = 'logs/{0}/{1}'.format(date, alias)
        self.cmd('mkdir -p {0}'.format(target_directory))

        # Move files
        for f in files:
            # Concatenate the date onto the filename as: <filename>_<time>.<extension>
            dated_name = f.split('.')[0] + '_' + self.time() + '.' + f.split('.')[1]
            # Move files to folders like: logs/<alias>/<date>/files...
            self.cmd('mv {0} {1}/{2}'.format(f, target_directory, dated_name))

    def echo_out(self, line):
        """
        Appends a line to the output file
        :param line: line of text (string)
        """
        with open(self.outputfile, "a") as output_file:
            output_file.write('{0}\n'.format(line))
            output_file.close()

    def cmd(self, command):
        return os.popen(command).read().rstrip('\n')

    def date(self):
        return self.cmd('date +"%Y-%m-%d"')

    def full_date(self):
        return self.cmd('date +"%Y-%m-%d"\' \'"%T"')

    def time(self):
        return self.cmd('date +%T')


class TestParser(object):
    def __init__(self, test_dirs=['/home/admin/git_cron/framework3/robot/suites']):
        self.test_dirs = test_dirs

    def print_all_info(self):
        """
        Prints .robot info for every robot file in self.test_dirs
        :return:
        """
        for robotfile in self.list_files():
            self.print_robot_info(robotfile)

    def print_robot_info(self, robotfile):
        """
        Prints .robot info to screen in this format:
        <test_file_name> : ['act-12345', 'act-23434', 'act-54355', ...]
        :param robotfile:
        :return:
        """
        testlink_numbers = self.list_testlink_numbers(self.list_lines(robotfile))
        print('{0} : {1}'.format(robotfile.split('/robot/')[1], testlink_numbers))

    def list_files(self):
        """
        Returns a list of all *.robot files in test directories
        :return:
        """
        matches = []
        for directory in self.test_dirs:
            for root, dirnames, filenames in os.walk(directory):
                for filename in fnmatch.filter(filenames, '*.robot'):
                    matches.append(os.path.join(root, filename))
        return matches

    def list_testlink_numbers(self, line_list):
        """
        :param line_list: list of lines (preferably from a .robot file)
        :return: Returns list of all instances of 'act-#####' in a list of strings
        """
        filestring = ' '.join(line_list)
        return list(set(re.findall('act-\d+', filestring, re.IGNORECASE)))

    def list_lines(self, robotfile):
        """
        Opens a file and reads lines into a list
        :param robotfile: .robot file
        :return: list of all the lines in the file
        """
        with open(robotfile) as source_file:
            line_list = [line.rstrip('\n') for line in source_file]
            source_file.close()
        return line_list


class InventoryParser(object):
    def __init__(self, host_dir='host', appliance_dir='appliance'):
        absolute_path = os.path.abspath('.')
        self.host_dir = '{0}/{1}'.format(absolute_path, host_dir)
        self.appliance_dir = '{0}/{1}'.format(absolute_path, appliance_dir)

    def _return_argument(self, argument):
        """
        Returns argument passed
        :param argument:
        :return: the value of the argument passed in
        """
        return argument

    def get_hosts(self, path=False):
        """
        Returns a dictionary of file names as keys and a dictionary of inventory attributes as value
        :param path: (boolean) If True, dictionary keys will be 'path/to/file.file', not default 'file.file'
        :return: dictionary of dictionaries
        """
        if path:
            method = self._return_argument
        else:
            method = self._filename_only
        return {method(invfile): self.get_host_attributes(invfile) for invfile in self.list_files(self.host_dir)}

    def get_appliances(self, path=False):
        """
        Returns a list dictionaries containing Appliance data.
        :return:
        """
        if path:
            method = self._return_argument
        else:
            method = self._filename_only
        return {method(invfile): self.get_appliance_attributes(invfile) for invfile in self.list_files(self.appliance_dir)}

    def print_inventory(self, path=False, hosts=True, appliances=True):
        """
        Prints info for every inv file in self.inv_dirs
        :return:
        """
        if hosts:
            print('**** HOST INVENTORY ****')
            pprint.pprint(self.get_hosts(path=path), width=190)
        if appliances:
            print('**** APPLIANCE INVENTORY ****')
            pprint.pprint(self.get_appliances(path=path), width=190)

    def print_host_info(self, invfile):
        """
        Prints host info
        :param invfile: host inventoryfile.py
        :return:
        """
        attribute_list = self.get_host_attributes(invfile)
        print('{0} : {1}'.format(invfile.split('/')[-1], attribute_list))

    def print_appliance_info(self, invfile):
        """
        Prints host info
        :param invfile: host inventoryfile.py
        :return:
        """
        attribute_list = self.get_appliance_attributes(invfile)
        print('{0} : {1}'.format(invfile.split('/')[-1], attribute_list))

    def list_files(self, inv_directory):
        """
        Returns a list of all *.py files in test directories
        :return:
        """
        matches = []
        for root, dirnames, filenames in os.walk(inv_directory):
            for filename in fnmatch.filter(filenames, '*.py'):
                matches.append(os.path.join(root, filename))
        return matches

    def find_full_path_from_filename(self, name):
        """
        Returns full path of inventory file
        :return:
        """
        for root, dirs, files in os.walk('.'):
            if name in files:
                pathname = os.path.join(root, name)
                return pathname[1:].lstrip('/')
        raise RuntimeError('Could not find the inventory file "{0}"'.format(name))

    def _filename_only(self, invfile):
        """
        :param invfile: full path to inventory file
        :return: filename (no path)
        """
        return invfile.split('/')[-1]

    def get_host_attributes(self, invfile):
        attribute_list = []
        line_list = self.list_lines(invfile)
        for attribute in ['name', 'ip', 'app', 'app_type']:
            attribute_list.append(self.get_attribute(attribute, line_list))
        return attribute_list

    def get_appliance_attributes(self, invfile):
        attribute_list = []
        line_list = self.list_lines(invfile)
        for attribute in ['hostname', 'appliance_ip']:
            attribute_list.append(self.get_attribute(attribute, line_list))
        return attribute_list

    def get_attribute(self, attribute, line_list):
        """
        :param attribute: the attribute name to get from an inventory file, like 'appliance_ip' etc.
        :param line_list: list of lines (preferably from a .py file)
        :return: Returns string like "'<attribute_name>': '<attribute_value'"
        """
        # for appliances get 'hostname' and 'applicance_ip'
        # for hosts get name, app_type, and ip
        filestring = ' '.join(line_list)
        result = re.search('\'{0}\': \'.*?\''.format(attribute), filestring, re.IGNORECASE)
        if result:
            return result.group(0)
        else:
            return '{0}: '.format(attribute)

    def get_value(self, invfile, attribute):
        """
        Returns value of attribute from inventory file
        :param invfile: full path to .py inventory file
        :param attribute: attribute to get value of
        :return: the value
        """
        line_list = self.list_lines(invfile)
        attribute_string = self.get_attribute(attribute, line_list)
        return attribute_string.split(':')[1].lstrip().replace("'", '')

    def find_appliance_file_from_hostname(self, name):
        """
        Returns the full absolute path of an appliance inventory file from its 'hostname'
        :param name: e.g. 'regresssky1.py'
        :return: e.g. '/home/leif/appliance/regresssky1.py'
        """
        all_appliances = self.list_files(self.appliance_dir)
        for appliance in all_appliances:
            hostname = self.get_value(appliance, 'hostname')
            if hostname == name:
                return appliance
        raise RuntimeError('Was unable to find inventory file containing hostname: {0}'.format(name))

    def find_host_file_from_name(self, name):
        """
        Returns the full absolute path of an appliance inventory file from its 'name'
        :param name: e.g. 'NSTLPAR18_nathan.py'
        :return: e.g. '/home/leif/hosts/NSTLPAR18_nathan.py'
        """
        all_hosts = self.list_files(self.host_dir)
        for host in all_hosts:
            hostname = self.get_value(host, 'name')
            if hostname == name:
                return host
        raise RuntimeError('Was unable to find inventory file containing name: {0}'.format(name))

    def list_lines(self, invfile):
        """
        Opens a file and reads lines into a list
        :param invfile: .py file
        :return: list of all the lines in the file
        """
        with open(invfile) as source_file:
            line_list = [line.rstrip('\n') for line in source_file]
            source_file.close()
        return line_list

# ***** Appliance Utility


class ApplianceController(object):
    def __init__(self, hostname, port=26, **update_cmds):
        """
        Run basic commands on an Appliance, do not use this to replace ApplianceLib for automation in framework3
        :param hostname: the hostname in the inventory file of the Appliance
        :param port: default is 26 for appliances
        :param update_cmds: additional key value pairs
        """
        # Gather ssh connection values from inventory file:
        parser = InventoryParser()
        if '.py' in hostname:
            invfile = parser.find_full_path_from_filename(hostname)
        else:
            invfile = parser.find_appliance_file_from_hostname(name=hostname)

        self.ipaddress = parser.get_value(invfile, 'appliance_ip')
        self.username = parser.get_value(invfile, 'ssh_user')
        self.password = parser.get_value(invfile, 'ssh_pass')
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

    def turn_on_scheduler(self):
        """
        Turns on the appliance scheduler
        :return:
        """
        return self.cmd('/act/bin/udstask setparameter -param enablescheduler -value 1')

    def turn_off_scheduler(self):
        """
        Turns off the appliance scheduler
        :return:
        """
        return self.cmd('/act/bin/udstask setparameter -param enablescheduler -value 0')

    def date(self):
        """
        Return the date, good for testing connection
        :return:
        """
        return self.cmd('date')

# ***** Command line functions and argument handling *****


def print_help():
    """
    I don't intend for QA to call 'python testcontroller.py' directly.
    INSTEAD I have created a bash script which does so, called 'rbc'
    All that rbc contains is:
    'python testcontroller.py $1 $2 $3 $4 $5 $6 $7 $8 $9'
    :return:
    """
    script_name = './rbc'
    print('')
    print('***********************************')
    print('Robot Controller --- ')
    print('Test Information:')
    print('{0} -tests (List all robot files and test cases covered by them)'.format(script_name))
    print('{0} -hosts (List all host inventory filenames to be used in aliases'.format(script_name))
    print('{0} -appliances (list all appliance inventory filenames to be used in aliases'.format(script_name))
    print('{0} -aliases (List alias names and docker/robot command assosciated)'.format(script_name))
    print('{0} -inventory (List all inventory files with paths)'.format(script_name))
    print('')
    print('Executing Tests:')
    print('{0} -a (Execute all tests in aliases file)'.format(script_name))
    print('{0} <alias> (To execute a single test)'.format(script_name))
    print('{0} <alias1> <alias2> <alias3> (execute 3 different tests)'.format(script_name))
    print('')
    print('Utility:')
    print('{0} -s1 <appliance_hostname/inventory filename> (turns on the appliance scheduler)'.format(script_name))
    print('{0} -s0 <appliance_hostname/inventory filename> (turns off the appliance scheduler)'.format(script_name))
    print('e.g. {0} -s1 mysky.py'.format(script_name))
    print('***********************************')

if __name__ == '__main__':
    args = sys.argv[1:]
    # If no arguments passed in, execute all tests
    if not args:
        print_help()
    else:
        if args[0].lower() in ['s1', '-s', '-s_1', '-s1']:
            try:
                if args[1].lower():
                    a = ApplianceController(args[1])
                    a.turn_on_scheduler()
                    date = a.date()
                    print('Appliance Scheduler Enabled at {0}'.format(date))
            except IndexError:
                raise RuntimeError('Please provide a hostname as second argument')
        elif args[0].lower() in ['s0', '-s_0', '-s0']:
            try:
                if args[1].lower():
                    a = ApplianceController(args[1])
                    a.turn_off_scheduler()
                    date = a.date()
                    print('Appliance Scheduler Disabled at {0}'.format(date))
            except IndexError:
                raise RuntimeError('Please provide a hostname as second argument')
        else:
            if args[0].lower() in ['h', '-h', '--h', '-help', '--help', 'help']:
                print_help()
            elif args[0].lower() in ['aliases', '-aliases']:
                b = AliasReader()
                b.print_aliases()
            elif args[0].lower() in ['inv', 'inventory', '-inv', '-inventory']:
                a = InventoryParser()
                a.print_inventory(path=True)
            elif args[0].lower() in ['-hosts', 'hosts']:
                a = InventoryParser()
                a.print_inventory(appliances=False)
            elif args[0].lower() in ['-appliance', '-appliances', 'appliances', 'appliance']:
                a = InventoryParser()
                a.print_inventory(hosts=False)
            elif args[0].lower() in ['tests', '-tests', 'robots']:
                a = TestParser()
                a.print_all_info()
            elif args[0].lower() in ['all', '-a', 'runall', '-runall', 'a', '-all']:
                print('** Test Controller | Executing all tests**')
                a = TestController()
                a.run_tests()
            else:
                a = TestController()
                # check that all aliases have commands
                for alias in args:
                    if alias not in a.aliases:
                        raise RuntimeError('alias {0} not found in alias list'.format(alias))
                # run all tests from aliases
                print('** Test Controller | Executing the following tests:')
                print(args)
                for alias in args:
                    if alias in a.aliases:
                        a.run_test(alias)


