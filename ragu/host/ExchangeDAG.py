from rf_inventory import get_appliance_variables, get_host_variables


variables = {'host_name': 'exchange',
             'user': 'Administrator',
             'password': '12!pass345',
             'app_type': 'Exchange',
             'app': 'ProdMB02',
             'ip': '172.27.13.111',
             'passive_ip1': '172.27.13.113',
             'active_ip': '172.27.13.112',
             'cluster_ip': '172.27.13.114',
             'variable_name': 'variable_value',
             'another_variable': 'another value'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
