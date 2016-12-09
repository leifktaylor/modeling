from rf_inventory import get_appliance_variables, get_host_variables


variables = {'host_name': 'Standalone',
             'user': 'Administrator',
             'password': '12!pass345',
             'app_type': 'Exchange',
             'ip': '172.27.13.110',
             'variable_name': 'variable_value',
             'another_variable': 'another value'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
