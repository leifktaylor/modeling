from rf_inventory import get_host_variables

variables = {'name': 'rh66db2',  # The name of the application, as it will be discovered by Actifio Appliance
             'ip': '172.27.13.128',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app': 'rh66db2',
             'app_type': 'Oracle',
             'apps': ['/', '/home', 'rh66db2'],
             'app_list': ['/', '/home', 'rh66db2'],
             'app_exclude': ['/'],
             'cluster_ip': '172.27.13.128',
             'racnodelist': '172.27.13.125',  # This can be ':' delimited for multiple entries
             'oracle_user': 'oracle',
             'oracle_pass': '12!pass345',  # Oracle user SSH Password, not oracle pw
             'oracle_sid': 'rh66db2',  # Name of Database to protect
             'oracle_home': '/database/oracle/app/oracle/product/11.2.0/dbhome_1',
             'oracle_path': '/database/oracle/app/oracle/product/11.2.0/dbhome_1/bin',
             }
provisioning_options = {'po_databasesid': 'achild',
                        'po_username': 'oracle',
                        'po_orahome': '/database/oracle/app/oracle/product/11.2.0/dbhome_1',
                        'po_tnsadmindir': '/database/oracle/app/oracle/product/11.2.0/dbhome_1/network/admin',
                        'po_totalmemory': '600',
                        'po_sgapct': '60',
                        }
variables.update(provisioning_options)


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)
