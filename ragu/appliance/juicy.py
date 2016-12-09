from rf_inventory import get_appliance_variables


variables = {'hostname': 'juicy',
             'appliance_ip': '172.16.13.210',
             'user': 'admin',
             'pass': 'password',
             'ssh_user': 'root',
             'ssh_pass': 'actifio2',
             'ssh_private_key_file': '',
             }


if __name__ == '__main__':
    print(get_variables(prepend='before', append='after', delimiter='|MiLeD|'))


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
