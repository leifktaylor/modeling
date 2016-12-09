from rf_inventory import get_appliance_variables
__author__ = 'katieboria'
import copy


def get_variables(prepend=None, append=None, delimiter='.'):
    """
    Format variables for Robot Framework tests.

    This will create a dictionary of variables in a way that Robot Framework can naturally read.
    :param prepend: String to put in front of variable keynames
    :param append: String to put at end of variable keynames
    :param delimiter: What to join the pends with. None-type object is not a valid input
    :return: Dictionary of variables that robot can read
    """
    base = {'hostname': 'wta29u29',
            'appliance_ip': '172.16.29.150',
            'user': 'admin',
            'pass': 'password',
            'ssh_user': 'root',
            'ssh_pass': 'actifio2',
            'ssh_private_key_file': '',
            }
    base['initialize'] = {'ip_address': base['appliance_ip'],
                          'hostname': base['hostname'],
                          'username': base['user'],
                          'password': base['pass'],
                          'ssh_username': base['ssh_user'],
                          'ssh_password': base['ssh_pass'],
                          'ssh_pkey': base['ssh_private_key_file'],
                          }
    # copy so variables don't cause recursive loop
    variables = copy.deepcopy(base)
    for old_key, value in base.items():
        key_components = [prepend, old_key, append]
        key = delimiter.join(filter(None, key_components))
        variables[key] = variables.pop(old_key)
    return variables

if __name__ == '__main__':
    print(get_variables(prepend='before', append='after', delimiter='|MiLeD|'))


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
