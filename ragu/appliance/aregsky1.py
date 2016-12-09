from rf_inventory import get_appliance_variables

# Either hostname or appliance_ip are required. Other inputs are optional because they have defaults.
variables = {'hostname': 'aregsky1',
             'appliance_ip': '172.27.4.20',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             'ssh_private_key_file': ''
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
