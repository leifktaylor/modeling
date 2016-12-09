from rf_inventory import get_appliance_variables
__author__ = 'katieboria'

# This is used for 7.1.x Automation Regresion

variables = {'hostname': 'cocktail',
             'appliance_ip': '172.27.4.101',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             'ssh_private_key_file': '',
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
