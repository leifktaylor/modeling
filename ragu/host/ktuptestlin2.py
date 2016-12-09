from rf_inventory import get_appliance_variables, get_host_variables
# Don't touch this host, it's evil.

# This host is for 6.2.x Automated Regression setup.  See Katie

variables = {'name': 'ktuptestlin2',
             'ip': '172.16.29.97',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app_type': '',
             'app': '/oob',
             'apps': ['/oob', '/cgvol1', '/cgvol2'],
             'app_list': ['/oob', '/cgvol1', '/cgvol2'],
             'app_exclude': ['/', '/boot'],
             }

def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
