from rf_inventory import get_host_variables

variables = {'name': 'rh71orafs5',
             'ip': '172.27.17.125',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app': 'babydb',
             'app_type': 'Oracle',
             'apps': ['/', '/home', 'babydb'],
             'app_list': ['/', '/home', 'babydb'],
             'app_exclude': ['/'],
             'cluster_ip': None,
             'racnodelist': None,  # This can be ':' delimited for multiple entries
             'oracle_user': 'oracle',
             'oracle_pass': 'oracle',  # Oracle user SSH Password, not oracle pw
             'oracle_sid': 'babydb',  # name of database
             'oracle_home': '/orahome/oracle/12.0.1/dbhome_1',
             'oracle_path': '/orahome/oracle/12.0.1/dbhome_1/bin',
             }

provisioning_options = {'po_databasesid': 'babychd',
                        'po_username': 'oracle',
                        'po_orahome': '/orahome/oracle/12.0.1/dbhome_1',
                        'po_tnsadmindir': '/orahome/oracle/12.0.1/dbhome_1/network/admin',
                        'po_totalmemory': '600',
                        'po_sgapct': '60',
                        }

variables.update(provisioning_options)


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)
