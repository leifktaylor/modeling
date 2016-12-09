from rf_inventory import get_host_variables

# this host is owned by Katie and Youssef please do not change


variables = {'name': 'bb07asm',
             'ip': '172.16.199.90',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app': '/',
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
