from rf_inventory import get_host_variables


variables = {'host_name': '2012regsql1',
             'user': 'Administrator',
             'password': '12!pass345',
             'app': 'mycg',
             'instance_name': 'SQL2012\\SQL2012INST',
             'target_instance': 'AUTOSQL2014\\SQLSERVER2014',
             'ip': '172.27.13.121',
             'cluster_ip': '172.27.13.123',
             'cg_members': 'New1,New2',
             'app_type': 'ConsistencyGroup',
             'variable_name': 'variable_value',
             'another_variable': 'another value'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
