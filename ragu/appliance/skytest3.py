from rf_inventory import get_appliance_variables

# Either hostname or appliance_ip are required. Other inputs are optional because they have defaults.
variables = {'hostname': 'skytest3',
             'appliance_ip': '172.16.116.155',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             'ssh_private_key_file': ''
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
