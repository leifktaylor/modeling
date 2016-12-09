from rf_inventory import get_host_variables


variables = {'host_name': '2012regsql2',
             'user': 'Administrator',
             'password': '12!pass345',
             'app_type': 'SqlServer',
             'instance_name': '2012REGSQL2\\STANDALONE2012',
             'named_instance_name': '2012REGSQL2\\SQL2014NAMINS',
             'ip': '172.27.13.122',
             'app': 'Prod_DB15'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
