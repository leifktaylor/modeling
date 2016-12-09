from rf_inventory import get_host_variables

# This host is for Oracle FS 7.1.x Automation Regression.  See Katie

variables = {'name': 'aregrh68orafs4',
             'ip': '172.27.4.71',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'user': 'root',
             'password': '12!pass345',
             'app': 'regdb',
             'apps': ['regdb', '/'],
             'app_type': 'Oracle',
             'cluster_ip': '172.27.4.71',
             'racnodelist': None,   # If system is NOT rac setup, set racnodelist, and volgroupname to None
             'volgroupname': None,  #
             'oracle_user': 'oracle',
             'oracle_pass': 'oracle',  # Oracle user SSH Password, not oracle pw
             'oracle_sid': 'regdb',  # name of database
             'oracle_home': '/orahome/oracle/11.0.2/dbhome_1',
             'oracle_path': '/orahome/oracle/11.0.2/dbhome_1/bin',
             }

provisioning_options = {'po_databasesid': 'achild',
                        'po_username': 'oracle',
                        'po_orahome': '/orahome/oracle/11.0.2/dbhome_1',
                        'po_tnsadmindir': '/orahome/oracle/11.0.2/dbhome_1/network/admin',
                        'po_totalmemory': '600',
                        'po_sgapct': '60',
                        }

variables.update(provisioning_options)


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
