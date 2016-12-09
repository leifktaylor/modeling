from rf_inventory import get_host_variables

# this host if for 7.0.x automation.  see katie

variables = {'name': 'bb5automation',
             'ip': '172.17.2.50',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app': '/oob',
             'apps': ['/oob', '/cgvol1', '/cgvol2'],
             'app_list': ['/oob', '/cgvol1', '/cgvol2'],
             'app_exclude': [''],
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
