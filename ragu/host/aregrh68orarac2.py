from rf_inventory import get_host_variables

# This host is for Oracle RAC 7.1.x Automation Regression.  See Katie

variables = {'name': 'aregrh68orarac2',
             'ip': '172.27.4.63',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app': 'yaydb',
             'apps': ['yaydb', '/'],
             'app_type': 'Oracle',
             'volgroupname': 'myvolgroup',
             'cluster_ip': '172.27.4.62',
             'racnodelist': '172.27.4.63',
             'oracle_user': 'oracle',
             'oracle_pass': 'oracle',  # Oracle user SSH Password, not oracle pw
             'oracle_sid': 'yaydb2',  # name of database
             'oracle_home': '/u01/app/oracle/product/12.1.0.2/db_1',
             'oracle_path': '/u01/app/oracle/product/12.1.0.2/db_1/bin',
             }

provisioning_options = {'po_databasesid': 'achild',
                        'po_username': 'oracle',
                        'po_orahome': '/u01/app/oracle/product/12.1.0.2/db_1',
                        'po_tnsadmindir': '/u01/app/oracle/product/12.1.0.2/db_1/network/admin',
                        'po_totalmemory': '600',
                        'po_sgapct': '60',
                        }

variables.update(provisioning_options)


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
