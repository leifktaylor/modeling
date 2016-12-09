from rf_inventory import get_appliance_variables
# Don't touch this; it's evil.

# This sky if for Automation Regression.  See Katie

variables = {'hostname': 'aregsky2',
             'appliance_ip': '172.27.4.220',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
