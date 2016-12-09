from rf_inventory import get_appliance_variables

<<<<<<< HEAD
# Either hostname or appliance_ip are required. Other inputs are optional because they have defaults.
variables = {'hostname': 'ktsky',
             'appliance_ip': '172.16.116.151',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             'ssh_private_key_file': ''
             }
=======

def get_variables(prepend=None, append=None, delimiter='.'):
    """
    Format variables for Robot Framework tests.
>>>>>>> 8ce8be7d4f721881635f0ca5b435ae7f744ddd5b


if __name__ == '__main__':
    print(get_variables(prepend='host', append='after', delimiter='|MiLeD|'))


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
