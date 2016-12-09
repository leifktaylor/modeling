from rf_inventory import get_host_variables
# Don't touch this host, it's evil.

# This host is for 7.1.x Automated Regression setup.  See Katie

variables = {'name': 'leif-lin',
             'ip': '172.27.17.9',
             'ssh_user': 'root',
             'ssh_pass': '12!pass345',
             'ssh_private_key_file': '',
             'app_type': 'VM',
             'app': '/oob',
             'apps': ['/oob', '/cgvol1', '/cgvol2'],
             'app_list': ['/', '/boot', '/oob', '/cgvol1', '/cgvol2'],
             'app_exclude': ['/', '/boot'],
             'vcenter_host': 'autovcsa.sqa.actifio.com',
             'vcenter_login': 'Administrator@vsphere.local',
             'vcenter_password': '12!Pass345',
             'esx_host': 'DevAutoBranch2',
             'datastore': 'SKY-LEIF'
             }


def get_variables(prepend=None, append=None, delimiter='.', base=variables, **kwargs):
    return get_host_variables(base=base, prepend=prepend, append=append, delimiter=delimiter, **kwargs)

if __name__ == '__main__':
    print(get_variables('pre', 'app', 'delim'))
