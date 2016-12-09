from rf_inventory import get_appliance_variables


variables = {'hostname': 'some_hostname',
             'appliance_ip': '86.7.53.09',
             'user': 'username to authenticate over REST/Desktop',
             'pass': 'password to authenticate over REST/Desktop',
             'ssh_user': 'username to authenticate over ssh',
             'ssh_pass': 'password to authenticate over ssh',
             'ssh_private_key_file': '/location/of/private/key.file'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_appliance_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
