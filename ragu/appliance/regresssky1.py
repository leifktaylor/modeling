from rf_inventory import get_appliance_variables
variables = {'hostname': 'regresssky1.sqa.actifio.com',
             'appliance_ip': '172.27.13.120',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)
