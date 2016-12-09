from rf_inventory import get_appliance_variables, get_host_variables

variables = {'name': 'NSTLPAR18_raghu',
             'ip': '172.27.8.84',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app': 'nathan',
             'app_type': 'Oracle',
             'apps': ['/', '/admin', 'nathan'],
             'app_list': ['/', '/admin', 'nathan'],
             'app_exclude': ['/'],
             'cluster_ip': None,
             'racnodelist': None,  # This can be ':' delimited for multiple entries
             'oracle_user': 'oracle',
             'oracle_pass': '12!pass345', #Oracle user SSH Password, not oracle pw
             'oracle_sid': 'nathan', #name of database
             'oracle_home': '/oracle/11.2.0/product/db_home',
             'oracle_path': '/oracle/11.2.0/product/db_home/bin',
             }

provisioning_options = {'po_databasesid': 'child1',
                        'po_username': 'oracle',
                        'po_orahome': '/oracle/11.2.0/product/db_home',
                        'po_tnsadmindir': '/oracle/11.2.0/product/db_home/network/admin',
                        'po_totalmemory': '600',
                        'po_sgapct': '60',
                        }

variables.update(provisioning_options)


def get_variables(prepend=None, append=None, delimiter='.', base=variables):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter)

