from rf_inventory import get_host_variables

variables = {'host_name': '2008regsql3',
             'user': 'Administrator',
             'password': '12!pass345',
             'app': 'DB1',
             'app_type': 'SqlServer',
             'cg_members': '',
             'instance_name': '2008REGSQL3',
             'child_app': 'Testing_25',
             'ip': '172.27.13.124',
             'cluster_ip': '',
             'mount_point': 'E:\\Automation\\MountPoint',
             'variable_name': 'variable_value',
             'another_variable': 'another value'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)
