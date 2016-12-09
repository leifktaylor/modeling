from rf_inventory import get_host_variables


variables = {'name': 'some_hostname',
             'ip': '86.7.53.09',
             'ssh_user': 'username to authenticate over ssh',
             'ssh_pass': 'password to authenticate over ssh',
             'ssh_private_key_file': '/location/of/private/key.file',
             'app': 'Primary default app to be used (capitalization matters)',
             'apps': ['list', 'of', 'protectable', 'apps'],
             'app_list': ['list of every app on host'],
             'app_exclude': ['list of apps to never protect'],
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
