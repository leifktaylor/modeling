from rf_inventory import get_appliance_variables

# DO NOT USE THIS FILE IT IS FOR THE JENKINS BUILD
variables = {'hostname': 'No_use',
             'appliance_ip': '86.75.30.9',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             'ssh_private_key_file': '',
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
