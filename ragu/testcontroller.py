import os
import sys
import re
import fnmatch
import re

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
#   invdrobot -V inv/host/oraclehost.py:host -V inv/appliance/mycds.py suites/orarac1+2/databasetest.robot
#   [linux] # this will run the database test on my linux inventory file and a sky
#   invdrobot -V inv/host/linuxoracle.py:host -V inv/appliance/mysky.py suites/orarac1+2/databasetest.robot
#
# 4) To execute all of the tests in the 'aliases' file, simply run: './rbc -a'
# 5) To execute a single test from the 'aliases' file, simply run: './rbc <aliasname>' (e.g. ./rbc aix)
# 6) If you want to execute some but not all, simply list the ones you want: './rbc alias1 alias3 alias5
# 7) For additional help and examples, use './rbc'
#
# Happy Testing!


class AliasReader(object):
    """
    Parses aliases file and puts contents into dictionary like:
    {'<alias name': '<command>', '<another_alias>': '<another command>', etc}
    """
    def __init__(self, alias_file='aliases'):
        # Check that aliases file exists:
        if not os.path.isfile(alias_file):
            print('No alias file was found, create a file called aliases in this folder like:')
            print('[some_alias_name]')
            print('<some command with invdrobot or robot>')
            print('[another_alias]')
            print('<some other invdrobot command>')
            with open(alias_file, "a") as af:
                af.write('[mysystem]\n')
                af.write('invdrobot -V inv/appliance/mycds.py -V inv/host/myoracle.py suites/host/mytest.robot\n')
                af.write('[anothersystem]\n')
                af.write('invdrobot ...\n')
                af.close()
            raise RuntimeError('No alias file found, created an alias file called aliases, with example')

        # Open aliases file and read lines
        with open(alias_file) as source_file:
            line_list = [line.rstrip('\n') for line in source_file]
            source_file.close()

        # Parse and place lines into dictionary
        alias_dict = {}
        for i in range(0, len(line_list)):
            match = re.search(r"\[([A-Za-z0-9_]+)\]", line_list[i])
            if match:
                alias_dict[match.group(1)] = line_list[i+1]
        self.aliases = alias_dict


class TestController(object):
    """
    Execute commands from aliases file and move log files to nested folders
    """
    def __init__(self, outputfile='console.out', output_append=True, alias_checking=False):
        """
        :param outputfile: file where console output from tests will go
        :param output_append: automatically output all test console output to outputfile
        :param alias_checking: confirm that aliases use invdrobot or robot command
        """
        self.aliases = AliasReader().aliases
        self.outputfile = outputfile
        # Append redirection to output file to all alias commands
        if output_append:
            for alias, command in self.aliases.items():
                self.aliases[alias] = '{0} >> {1} 2>&1'.format(command, self.outputfile)
            print(self.aliases)

        # Check that robot or invdrobot is being called in command
        if alias_checking:
            raised = False
            for alias, command in self.aliases.items():
                if 'invdrobot' not in command:
                    if 'robot' not in command:
                        print('Warning [{0}] must use invdrobot or robot to create logs! Fix aliases file'.format(alias))
                        raised = True
            if raised:
                raise RuntimeError('Correct aliases file to use invdrobot or robot command')

    def run_test(self, alias):
        # Echo commencing line into outputfile
        start_date = self.date()
        self.echo_out('**** STARTING TEST: {0} at {1} ****'.format(alias, self.full_date()))

        # Execute test
        invdrobot_command = self.aliases[alias]
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
                raise RuntimeError('{0} not found! Aborting'.format(f))

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
    def __init__(self, test_dirs=['/Users/actifioadmin/PycharmProjects/framework3/robot/suites']):
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

    def print_all_info(self):
        """
        Prints info for every inv file in self.inv_dirs
        :return:
        """
        print('**** HOST INVENTORY ****')
        for invfile in self.list_files(self.host_dir):
            self.print_host_info(invfile)
        print('')
        print('**** APPLIANCE INVENTORY ****')
        for invfile in self.list_files(self.appliance_dir):
            self.print_appliance_info(invfile)

    def print_host_info(self, invfile):
        """
        Prints host info
        :param invfile: host inventoryfile.py
        :return:
        """
        attribute_list = self.get_host_attributes(invfile)
        print('{0} : {1}'.format(invfile, attribute_list))

    def print_appliance_info(self, invfile):
        """
        Prints host info
        :param invfile: host inventoryfile.py
        :return:
        """
        attribute_list = self.get_appliance_attributes(invfile)
        print('{0} : {1}'.format(invfile, attribute_list))

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
        :return: Returns list of all instances of 'act-#####' in a list of strings
        """
        # for appliances get 'hostname' and 'applicance_ip'
        # for hosts get name, app_type, and ip
        filestring = ' '.join(line_list)
        result = re.search('\'{0}\': \'.*?\''.format(attribute), filestring, re.IGNORECASE)
        if result:
            return result.group(0)
        else:
            return '{0}: '.format(attribute)

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
    print('***********************************')
    print('Robot Controller --- Help')
    print('Test Information:')
    print('{0} tests (List all robot files and test cases covered by them)'.format(script_name))
    print('{0} inventory (List all inventory files)'.format(script_name))
    print('')
    print('Executing Tests:')
    print('{0} -a (Execute all tests in aliases file)'.format(script_name))
    print('{0} <alias> (To execute a single test)'.format(script_name))
    print('{0} <alias1> <alias2> <alias3> (execute 3 different tests)'.format(script_name))
    print('***********************************')

if __name__ == '__main__':
    args = sys.argv[1:]
    # If no arguments passed in, execute all tests
    if not args:
        print_help()
    else:
        if args[0].lower() in ['h', '-h', '--h', '-help', '--help', 'help']:
            print_help()
        elif args[0].lower() in ['inv', 'inventory', '-inv', '-inventory']:
            a = InventoryParser()
            a.print_all_info()
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


