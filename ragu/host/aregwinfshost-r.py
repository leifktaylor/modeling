from rf_inventory import get_host_variables
# Don't touch this host, it's evil.

# This host is for 7.1.x Automated Regression Setup.  See Katie

variables = {'name': 'aregwinfshost-r',
             'ip': '172.27.4.46',
             'ssh_user': 'Administrator',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app_type': '',
             'app': 'W:\\',
             'apps': ['W:\\', 'U:\\', 'V:\\'],
             'app_list': ['C:\\', 'E:\\', 'U:\\', 'V:\\', 'X:\\'],
             'app_exclude': ['C:\\', 'E:\\']
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
