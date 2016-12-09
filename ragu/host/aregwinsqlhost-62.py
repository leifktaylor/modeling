from rf_inventory import get_host_variables
# Don't touch this host, it's evil.

# This host is for Automated Regression Setup.  See Katie

variables = {'host_name': 'aregwinsqlhost-62',
             'user': 'Administrator',
             'password': '12!pass345',
             'app': 'DB01',
             'app_type': 'SqlServer',
             'cg_members': '',
             'instance_name': 'AREGWINFSHOST-6',
             'ip': '172.27.4.191',
             'mount_point': 'X:\\Automation\\MountPoint'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
