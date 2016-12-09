from rf_inventory import get_host_variables
# Don't touch this host, it's evil.

# This host is for 7.1.x Automated Regression Setup.  See Katie

variables = {'name': 'aregwinfshost',
             'ip': '172.27.4.45',
             'ssh_user': 'Administrator',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app': 'W:\\',
             'apps': ['W:\\', 'U:\\', 'V:\\'],
             'app_list': ['C:\\', 'E:\\', 'U:\\', 'V:\\', 'X:\\'],
             'app_exclude': ['C:\\', 'E:\\'],

             'user': 'Administrator',
             'password': '12!pass345',
             'db_app': 'DB01',
             'app_type': 'SqlServer',
             'cg_members': '',
             'instance_name': 'AREGWINFSHOST',
             'mount_point': 'W:\\Automation\\MountPoint'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
