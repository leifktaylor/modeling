#!/usr/bin/env python
from __future__ import print_function, division, unicode_literals, absolute_import
from appliance_base import ApplianceBase
from framework3 import appliance
from robot.api import logger as robot_logger
import logging
import re

# Known SVC Errors


class SVCUniquenessError(Exception):
    """ CMMVC6035E The action failed as the object already exists. """
    # CMMVC6071E The VDisk-to-host mapping was not created because the VDisk is already mapped to a host.


class SVCUnknownObject(Exception):
    """ CMMVC5753E The specified object does not exist or is not a suitable candidate. """
    # CMMVC5842E The action failed because an object that was specified in the command does not exist.


class SVCUnsupportedParameter(Exception):
    """ CMMVC5709E [-someparam] is not a supported parameter. """


class SVCInvalidCommand(Exception):
    """ CMMVC5987E [non-command] is not a valid command line option. """


class SVCCannotDelete(Exception):
    """ CMMVC5818E The managed disk group was not deleted because there is at least one MDisk in the group. """


svc_delim = '%'


class SVCLib(ApplianceBase):
    def __init__(self, *args, **kwargs):
        """
        Super-inherited from Appliance.
        :param args:
        :param kwargs:
        :return:
        """
        super(SVCLib, self).__init__(*args, **kwargs)
        robot_logger.debug('Initialized SVCLib')

    @staticmethod
    def table_parse(raw_stdout):
        """
        Parses a delimited svcinfo return and returns a dictionary.
        Takes the stdout response (a list of lines) from a.raw and converts to a dictionary of kv pairs.
        :param raw_stdout: stdout from a.raw
        :return: list of dictionaries
        """
        # If nothing in stdout
        if not raw_stdout:
            logging.debug('Nothing to parse')
            return raw_stdout
        # pop out the header line to use as dictionary keys
        delimited_headers = raw_stdout.pop(0)
        headers = delimited_headers.split(svc_delim)
        # zip dictionary from headers and values
        return_list = []
        for line in raw_stdout:
            return_list.append(dict(zip(headers, line.split(svc_delim))))
        return return_list

    @staticmethod
    def single_entry_parse(raw_stdout):
        if not raw_stdout:
            logging.debug('Nothing to parse')
            return raw_stdout
        # zip dictionary from lines
        return_dict = {}
        for line in raw_stdout:
            try:
                value = line.split(svc_delim)[1]
            except IndexError:
                value = ''
            return_dict[line.split(svc_delim)[0]] = value
        return [return_dict]

    @staticmethod
    def kwargs_to_params(**kwargs):
        arg_list = []
        for key, value in kwargs.items():
            if key == 'argument':
                arg_list.append(value)
            else:
                arg_list.append('-{0} {1}'.format(str(key), str(value)))
        arg_string = ' '.join(arg_list)
        return arg_string

    @staticmethod
    def raise_svc_error(stderr_list, rc):
        """
        Takes stderr output from 'ApplianceLib.a.raw' and raises appropriate error
        :param stderr: stderr from raw cli output
        :return:
        """
        if rc != 0:
            # stderr is returned as a list with one item, get the string value of that item
            # if stderr is empty, raise an unknown runtime error
            try:
                stderr = stderr_list[0]
            except IndexError:
                raise RuntimeError('Unknown error, stderr response empty')
            # Check for SVC error codes:
            if 'CMMVC6035E' in stderr or 'CMMVC6071E' in stderr:
                raise SVCUniquenessError(stderr)
            elif 'CMMVC5753E' in stderr or 'CMMVC5842E' in stderr:
                raise SVCUnknownObject(stderr)
            elif 'CMMVC5709E' in stderr:
                raise SVCUnsupportedParameter(stderr)
            elif 'CMMVC5987E' in stderr:
                raise SVCInvalidCommand(stderr)
            elif 'CMMVC5818E' in stderr:
                raise SVCCannotDelete(stderr)
            else:
                raise RuntimeError(stderr)

    def svcinfo_cmd(self, command):
        """
        Takes string such as 'lshost' and converts to:
        self.a.raw('/compass/bin/svcinfo lshost -delim svc_delim ...extra kw args')
        :param command: e.g. lsvdiskhostmap, lshost, lsmdisk, etc...
        :return: stdout response from raw cli (list of lines)
        """
        # Argument must be the last item in an svc command
        # Delim param+value is inserted directly after the command name to prevent issues
        split_command = command.split()
        split_command.insert(1, '-delim {0}'.format(svc_delim))
        command_with_delim = ' '.join(split_command)
        command_string = '/compass/bin/svcinfo {0}'.format(command_with_delim)
        # determine if argument at end of command string
        argument_in_command = False
        if command_string.split()[-1].isdigit():
            if '-' not in command_string.split()[-2]:
                argument_in_command = True
        # execute raw cli command
        stdout, err, rc = self.a.raw(command_string)
        # Handle error if there is one
        self.raise_svc_error(err, rc)
        # SVCInfo will return a table if no argument is given, or a single entry if an argument is given
        # due to this, returns must be parsed in two completely different ways.
        if argument_in_command:
            data_table = self.single_entry_parse(stdout)
        else:
            data_table = self.table_parse(stdout)
        return data_table

    def svctask_cmd(self, command, **kwargs):
        """
        Takes string such as 'mkvdisk' and converts to:
        self.a.raw('/compass/bin/svctask mkvdisk ..extra kw args')
        For commands that have an argument, e.g. rmvdisk <vdiskid>
        Invoke this command as: svctask_cmd('rmvdisk', argument=vdiskid)
        :param command: e.g. 'rmvdisk', 'mkvdisk', etc
        :param kwargs: parameters like 'image=<someimage>'
        :return: stdout response from raw cli (list of lines)
        """
        # execute raw cli command
        stdout, err, rc = self.a.raw('/compass/bin/svctask {0}'.format(command))
        # Check for errors:
        self.raise_svc_error(err, rc)
        return stdout

    def add_mdiskgrp(self, name='automdiskgrp', ext=1024):
        """
        Uses svtask mkmdiskgrp to create an mdisk group.
        Creates an mdisk group of given name
        :param name: mdiskgrp name
        :param ext: extent size (e.g. 1024)
        :return: mdiskgrp id
        """
        try:
            stdout = self.svctask_cmd('mkmdiskgrp -name {0} -ext {1}'.format(name, ext))
            # Parse mdiskgrp_id from response
            mdiskgrp_id = re.search(r'\d+', stdout[0]).group(0)
        except SVCUniquenessError:
            mdiskgrp_id = self.svcinfo_cmd('lsmdiskgrp -filtervalue name={0}'.format(name))[0]['id']
        return mdiskgrp_id

    def absent_mdiskgrp(self, mdiskgrp):
        """
        Idempotently remove mdiskgrp by id or name
        :return:
        """
        try:
            self.svctask_cmd('rmmdiskgrp {0}'.format(mdiskgrp))
        except SVCUnknownObject:
            pass

    def select_unmanaged_mdisk(self, desired_capacity=10):
        """
        Selects an unmanaged mdisk close to the desired capacity of 10gb,
        works only on CDS.
        :param desired_capacity: desired capacity in GB
        :return: mdisk id
        """
        # Get list of mdisks
        mdisklist = self.search_mdisk()
        # Search for unmanaged mdisk of desired_capacity in list of dictionaries
        for mdisk in mdisklist:
            # Parse out the value of each column in this row
            if mdisk['mode'] == 'unmanaged':
                if mdisk['capacity'] == str(desired_capacity) + '.0GB':
                    return mdisk['id']
        # If no unmanaged mdisk of desired_capacity found
        raise RuntimeError('No unmanaged MDisk of {0}.0GB found'.format(str(desired_capacity)))

    def get_svchostid_from_udshostid(self, hostid):
        """
        Gets svchost id from 'svcinfo lshost' based off of the 'svcname' returned from
        'udsinfo lshost <hostid>'
        :param hostid: udshostid (from udsinfo lshost)
        :return: svchostid (from svcinfo lshost)
        """
        try:
            svcname = self.find_host(argument=hostid).parse(k='svcname')
        except KeyError:
            raise RuntimeError('Host has no svcname')
        svchostid = self.search_host(filtervalue='name={0}'.format(svcname))[0]['id']
        return svchostid