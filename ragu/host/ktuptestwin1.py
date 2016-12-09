from rf_inventory import get_host_variables
# Don't touch this host, it's evil.

# This host is for Automated Regression Setup.  See Katie

variables = {'name': 'ktuptestwin1',
             'ip': '172.16.29.95',
             'ssh_user': 'Administrator',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app_type': '',
             'app': 'E:\\',
             'apps': ['E:\\', 'U:\\', 'V:\\'],
             'app_list': ['C:\\', 'E:\\', 'U:\\', 'V:\\', 'F:\\'],
             'app_exclude': ['C:\\'],
             'user':    'Administrator',
             'password':  '12!pass345',
             'db_app':    'DB01',
             'db_type': 'SqlServer',
             'cg_members': '',
             'instance_name': 'KTUPTESTWIN1',
             'mount_point': 'W:\\Automation\\MountPoint'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
