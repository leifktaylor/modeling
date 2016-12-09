from rf_inventory import get_host_variables


variables = {'host_name': 'sql2014-vm1',
             'user': 'Administrator',
             'password': '12!pass345',
             'instance_name': '',
             'target_instance': '',
             'ip': '172.27.4.21',
             'cluster_ip': '172.27.4.23',
             'congrpmembers': 'New1,New2',
             'app_type': 'SqlServer',
             'app': 'New2',
             #'app_type': 'ConsistencyGroup',
             'variable_name': 'variable_value',
             'another_variable': 'another value'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
