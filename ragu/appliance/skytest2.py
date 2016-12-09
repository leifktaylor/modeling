from rf_inventory import get_appliance_variables

<<<<<<< HEAD
variables = {'hostname': 'skytest2',
             'appliance_ip': '172.16.116.154',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             'ssh_private_key_file': '',
             }
=======

def get_variables(prepend=None, append=None, delimiter='.'):
    """
    Format variables for Robot Framework tests.

    This will create a dictionary of variables in a way that Robot Framework can naturally read.
    :param prepend: String to put in front of variable keynames
    :param append: String to put at end of variable keynames
    :param delimiter: What to join the pends with. None-type object is not a valid input
    :return: Dictionary of variables that robot can read
    """
    # These are the variables that can be referenced in robot framework.
    base = {'hostname': 'skytest2',
            'appliance_ip': '172.16.116.154',
            'user': 'admin',
            'pass': 'password',
            'ssh_user': 'root',
            'ssh_pass': 'actifio2',
            'ssh_private_key_file': '',
            }
    # The initialize dictionary is fed to ApplianceLib. The purpose of this is to allow different resources to expose
    # different levels of information to the library.
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
>>>>>>> 8ce8be7d4f721881635f0ca5b435ae7f744ddd5b

if __name__ == '__main__':
    print(get_variables(prepend='host', append='after', delimiter='|MiLeD|'))


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
